#!/usr/bin/env python3

# ============================================================
# PW4 - ROS2 AI-Based Object Detection
# Phase 3: YOLO Green Ball Detection
#
# Package : mindspark_robot
# Node    : yolo_green_ball_node
# Model   : yolo11n.pt
#
# Subscribe:
#   /camera/image_raw
#   sensor_msgs/msg/Image
#
# Publish:
#   /yolo/green_ball
#   std_msgs/msg/String
#
# Detection Method:
#   1. YOLO11n Sports Ball Detection
#   2. OpenCV HSV Green Colour Verification
#   3. Select Highest Confidence Green Ball
#   4. Publish Ball Centre Coordinates
#
# Press Q to exit
# ============================================================

import time

import cv2
import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

from ultralytics import YOLO


class YOLOGreenBallNode(Node):

    def __init__(self):

        super().__init__('yolo_green_ball_node')

        # ====================================================
        # 1. Camera Configuration
        # ====================================================

        self.frame_width = 320
        self.frame_height = 240

        # ====================================================
        # 2. YOLO Configuration
        # ====================================================

        self.model_path = 'yolo11n.pt'

        self.conf_threshold = 0.40
        self.img_size = 640

        # COCO Sports Ball Class
        self.target_class = 32

        # CUDA GPU
        self.device = 0

        # ====================================================
        # 3. HSV Green Colour Configuration
        # ====================================================

        self.lower_green = np.array(
            [35, 70, 50],
            dtype=np.uint8
        )

        self.upper_green = np.array(
            [85, 255, 255],
            dtype=np.uint8
        )

        # Minimum green pixel percentage
        self.green_ratio_threshold = 0.30

        # ====================================================
        # 4. Load YOLO Model
        # ====================================================

        self.get_logger().info(
            'Loading YOLO11n pretrained model...'
        )

        self.model = YOLO(self.model_path)

        self.get_logger().info(
            'YOLO Model Loaded Successfully'
        )

        # ====================================================
        # 5. OpenCV Bridge
        # ====================================================

        self.bridge = CvBridge()

        # ====================================================
        # 6. Frame Variables
        # ====================================================

        self.latest_frame = None

        self.new_frame_available = False

        # ====================================================
        # 7. ROS2 Subscriber
        # ====================================================

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # ====================================================
        # 8. ROS2 Publisher
        # ====================================================

        self.publisher = self.create_publisher(
            String,
            '/yolo/green_ball',
            10
        )

        # ====================================================
        # 9. FPS Monitoring
        # ====================================================

        self.frame_count = 0

        self.start_time = time.perf_counter()

        self.current_fps = 0.0

        # ====================================================
        # 10. ROS2 Processing Timer
        # ====================================================

        self.timer = self.create_timer(
            0.01,
            self.process_frame
        )

        # ====================================================
        # 11. Startup Information
        # ====================================================

        self.get_logger().info(
            '===================================='
        )

        self.get_logger().info(
            'PW4 - YOLO Green Ball Detection'
        )

        self.get_logger().info(
            '===================================='
        )

        self.get_logger().info(
            f'Model: {self.model_path}'
        )

        self.get_logger().info(
            'Target: Sports Ball (Class 32)'
        )

        self.get_logger().info(
            f'Confidence Threshold: {self.conf_threshold}'
        )

        self.get_logger().info(
            f'Green Ratio Threshold: '
            f'{self.green_ratio_threshold:.2f}'
        )

        self.get_logger().info(
            'Waiting for camera images...'
        )

    # ========================================================
    # 12. Receive ROS2 Camera Image
    # ========================================================

    def image_callback(self, msg):

        try:

            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

            # Ensure consistent image resolution
            if (
                frame.shape[1] != self.frame_width
                or frame.shape[0] != self.frame_height
            ):

                frame = cv2.resize(
                    frame,
                    (
                        self.frame_width,
                        self.frame_height
                    )
                )

            # Store newest camera frame
            self.latest_frame = frame

            self.new_frame_available = True

        except Exception as e:

            self.get_logger().error(
                f'Image conversion error: {e}'
            )

    # ========================================================
    # 13. Check Green Colour in Bounding Box
    # ========================================================

    def calculate_green_ratio(
        self,
        frame,
        x1,
        y1,
        x2,
        y2
    ):

        # Extract bounding box region
        roi = frame[y1:y2, x1:x2]

        if roi.size == 0:

            return 0.0

        # Convert BGR to HSV
        hsv_roi = cv2.cvtColor(
            roi,
            cv2.COLOR_BGR2HSV
        )

        # Apply HSV green threshold
        green_mask = cv2.inRange(
            hsv_roi,
            self.lower_green,
            self.upper_green
        )

        # Create circular region inside ROI
        # to reduce background influence

        height, width = green_mask.shape

        circle_mask = np.zeros(
            (height, width),
            dtype=np.uint8
        )

        centre = (
            width // 2,
            height // 2
        )

        radius = max(
            1,
            min(width, height) // 2
        )

        cv2.circle(
            circle_mask,
            centre,
            radius,
            255,
            -1
        )

        # Count green pixels within circle
        valid_mask = cv2.bitwise_and(
            green_mask,
            circle_mask
        )

        green_pixels = cv2.countNonZero(
            valid_mask
        )

        total_pixels = cv2.countNonZero(
            circle_mask
        )

        if total_pixels == 0:

            return 0.0

        green_ratio = (
            green_pixels / total_pixels
        )

        return green_ratio

    # ========================================================
    # 14. Process YOLO Detection
    # ========================================================

    def process_frame(self):

        # No camera frame available
        if self.latest_frame is None:

            return

        # Process only a new frame
        if not self.new_frame_available:

            return

        # Get latest frame
        frame = self.latest_frame.copy()

        self.new_frame_available = False

        # ----------------------------------------------------
        # A. Run YOLO Inference
        # ----------------------------------------------------

        results = self.model.predict(
            source=frame,
            conf=self.conf_threshold,
            imgsz=self.img_size,
            classes=[self.target_class],
            device=self.device,
            verbose=False
        )

        result = results[0]

        # ----------------------------------------------------
        # B. Detection Variables
        # ----------------------------------------------------

        best_ball = None

        best_confidence = -1.0

        green_ball_count = 0

        annotated_frame = frame.copy()

        frame_height, frame_width = frame.shape[:2]

        # ----------------------------------------------------
        # C. Process Each YOLO Sports Ball
        # ----------------------------------------------------

        for box in result.boxes:

            # Bounding box coordinates
            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            # Ensure coordinates are inside image
            x1 = max(0, min(x1, frame_width))
            x2 = max(0, min(x2, frame_width))

            y1 = max(0, min(y1, frame_height))
            y2 = max(0, min(y2, frame_height))

            if x2 <= x1 or y2 <= y1:

                continue

            # YOLO confidence
            confidence = float(
                box.conf[0].item()
            )

            # Calculate green pixel ratio
            green_ratio = self.calculate_green_ratio(
                frame,
                x1,
                y1,
                x2,
                y2
            )

            # Calculate ball centre
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # -----------------------------------------------
            # D. Verify Green Ball
            # -----------------------------------------------

            if green_ratio >= self.green_ratio_threshold:

                green_ball_count += 1

                # Draw green bounding box
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                # Draw centre point
                cv2.circle(
                    annotated_frame,
                    (cx, cy),
                    4,
                    (0, 0, 255),
                    -1
                )

                # Display object information
                label = (
                    f'GREEN BALL '
                    f'{confidence:.2f} '
                    f'G:{green_ratio:.0%}'
                )

                cv2.putText(
                    annotated_frame,
                    label,
                    (x1, max(15, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 0),
                    1
                )

                cv2.putText(
                    annotated_frame,
                    f'({cx}, {cy})',
                    (x1, min(y2 + 15, frame_height - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 255),
                    1
                )

                # Select highest-confidence green ball
                if confidence > best_confidence:

                    best_confidence = confidence

                    best_ball = (cx, cy)

            else:

                # Non-green sports ball
                cv2.rectangle(
                    annotated_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 0, 255),
                    1
                )

                cv2.putText(
                    annotated_frame,
                    f'REJECTED G:{green_ratio:.0%}',
                    (x1, max(15, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 255),
                    1
                )

        # ----------------------------------------------------
        # E. Publish ROS2 Detection Result
        # ----------------------------------------------------

        detection_msg = String()

        if best_ball is not None:

            cx, cy = best_ball

            detection_msg.data = (
                f'DETECTED: x={cx}, y={cy}'
            )

        else:

            detection_msg.data = 'NOT DETECTED'

        self.publisher.publish(
            detection_msg
        )

        # ----------------------------------------------------
        # F. Calculate Detection FPS
        # ----------------------------------------------------

        self.frame_count += 1

        elapsed = (
            time.perf_counter()
            - self.start_time
        )

        if elapsed >= 5.0:

            self.current_fps = (
                self.frame_count / elapsed
            )

            self.get_logger().info(
                f'YOLO Green Ball FPS: '
                f'{self.current_fps:.2f}'
            )

            self.frame_count = 0

            self.start_time = time.perf_counter()

        # ----------------------------------------------------
        # G. Display Information
        # ----------------------------------------------------

        cv2.putText(
            annotated_frame,
            f'FPS: {self.current_fps:.1f}',
            (10, 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f'Green Balls: {green_ball_count}',
            (10, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )

        # ----------------------------------------------------
        # H. Display Video
        # ----------------------------------------------------

        cv2.imshow(
            'PW4 - YOLO Green Ball Detection',
            annotated_frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):

            self.get_logger().info(
                'Stopping YOLO Green Ball Detection'
            )

            self.timer.cancel()

            rclpy.try_shutdown()

    # ========================================================
    # 15. Cleanup
    # ========================================================

    def destroy_node(self):

        cv2.destroyAllWindows()

        super().destroy_node()


# ============================================================
# Main Function
# ============================================================

def main(args=None):

    rclpy.init(args=args)

    node = None

    try:

        node = YOLOGreenBallNode()

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        if node is not None:

            node.destroy_node()

        if rclpy.ok():

            rclpy.shutdown()


if __name__ == '__main__':

    main()