#!/usr/bin/env python3

# ============================================================
# PW4 - ROS2 AI-Based Object Detection
# Phase 2: Sports Ball Detection Using YOLO11
#
# Package : mindspark_robot
# Node    : yolo_sports_ball_node
# Model   : yolo11n.pt
# Dataset : COCO
#
# Target Class:
#   Sports Ball = Class ID 32
#
# Features:
#   - Real-time webcam capture
#   - Sports ball detection only
#   - Bounding box visualization
#   - Confidence score
#   - Ball centre coordinates (X,Y)
#   - Detection FPS monitoring
#
# Press Q to exit
# ============================================================

import time
import cv2

import rclpy
from rclpy.node import Node

from ultralytics import YOLO


class YOLOSportsBallNode(Node):

    def __init__(self):

        super().__init__('yolo_sports_ball_node')

        # ====================================================
        # 1. Camera Configuration
        # ====================================================

        self.camera_id = 0

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

        # GPU
        self.device = 0

        # ====================================================
        # 3. Load YOLO Model
        # ====================================================

        self.get_logger().info(
            'Loading YOLO11 Sports Ball Detection Model...'
        )

        self.model = YOLO(self.model_path)

        self.get_logger().info(
            'YOLO11 Model Loaded Successfully'
        )

        # ====================================================
        # 4. Open Camera
        # ====================================================

        self.cap = cv2.VideoCapture(
            self.camera_id,
            cv2.CAP_V4L2
        )

        if not self.cap.isOpened():

            raise RuntimeError(
                'Cannot open webcam'
            )

        # Set MJPEG format
        self.cap.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*'MJPG')
        )

        # Set camera resolution
        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.frame_width
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.frame_height
        )

        # Request 30 FPS
        self.cap.set(
            cv2.CAP_PROP_FPS,
            30
        )

        # ====================================================
        # 5. FPS Monitoring
        # ====================================================

        self.frame_count = 0

        self.start_time = time.perf_counter()

        self.current_fps = 0.0

        # ====================================================
        # 6. ROS2 Timer
        # ====================================================

        self.timer = self.create_timer(
            0.01,
            self.detect_ball
        )

        # ====================================================
        # 7. Startup Information
        # ====================================================

        self.get_logger().info(
            '===================================='
        )

        self.get_logger().info(
            'PW4 - YOLO Sports Ball Detection'
        )

        self.get_logger().info(
            '===================================='
        )

        self.get_logger().info(
            f'Model: {self.model_path}'
        )

        self.get_logger().info(
            f'Target Class: {self.target_class}'
        )

        self.get_logger().info(
            f'Confidence Threshold: {self.conf_threshold}'
        )

        self.get_logger().info(
            f'Inference Device: CUDA {self.device}'
        )

        self.get_logger().info(
            'Press Q to exit'
        )

    # ========================================================
    # Sports Ball Detection
    # ========================================================

    def detect_ball(self):

        # ----------------------------------------------------
        # 1. Capture Frame
        # ----------------------------------------------------

        ret, frame = self.cap.read()

        if not ret:

            self.get_logger().warning(
                'Failed to capture frame'
            )

            return

        # ----------------------------------------------------
        # 2. Run YOLO Inference
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
        # 3. Count Detected Balls
        # ----------------------------------------------------

        ball_count = len(result.boxes)

        # ----------------------------------------------------
        # 4. Draw YOLO Bounding Boxes
        # ----------------------------------------------------

        annotated_frame = result.plot()

        # ----------------------------------------------------
        # 5. Extract Ball Information
        # ----------------------------------------------------

        for box in result.boxes:

            # Bounding box coordinates
            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0].tolist()
            )

            # Confidence score
            confidence = float(
                box.conf[0].item()
            )

            # Calculate ball centre
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # -----------------------------------------------
            # Draw Ball Centre
            # -----------------------------------------------

            cv2.circle(
                annotated_frame,
                (cx, cy),
                4,
                (0, 0, 255),
                -1
            )

            # -----------------------------------------------
            # Display Centre Coordinates
            # -----------------------------------------------

            cv2.putText(
                annotated_frame,
                f'({cx}, {cy})',
                (x1, min(y2 + 18, self.frame_height - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 255),
                1
            )

        # ----------------------------------------------------
        # 6. Calculate Detection FPS
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
                f'Detection FPS: {self.current_fps:.2f}'
            )

            self.frame_count = 0

            self.start_time = time.perf_counter()

        # ----------------------------------------------------
        # 7. Display Detection Information
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
            f'Balls: {ball_count}',
            (10, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )

        # ----------------------------------------------------
        # 8. Display Video
        # ----------------------------------------------------

        cv2.imshow(
            'PW4 - YOLO Sports Ball Detection',
            annotated_frame
        )

        # ----------------------------------------------------
        # 9. Keyboard Control
        # ----------------------------------------------------

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):

            self.get_logger().info(
                'Stopping Sports Ball Detection'
            )

            self.timer.cancel()

            rclpy.try_shutdown()

    # ========================================================
    # Cleanup
    # ========================================================

    def destroy_node(self):

        if hasattr(self, 'cap'):

            if self.cap.isOpened():

                self.cap.release()

        cv2.destroyAllWindows()

        super().destroy_node()


# ============================================================
# Main Function
# ============================================================

def main(args=None):

    rclpy.init(args=args)

    node = None

    try:

        node = YOLOSportsBallNode()

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    except Exception as e:

        print(f'YOLO Sports Ball Node Error: {e}')

    finally:

        if node is not None:

            node.destroy_node()

        if rclpy.ok():

            rclpy.shutdown()


if __name__ == '__main__':

    main()