#!/usr/bin/env python3

# ============================================================
# PW4 - ROS2 AI-Based Object Detection
# Phase 1: General Object Detection Using YOLO11
#
# Package : mindspark_robot
# Node    : yolo_detection_node
# Model   : yolo11n.pt
#
# Features:
#   - Real-time webcam capture
#   - Multi-class object detection
#   - Bounding box visualization
#   - Class label and confidence score
#   - FPS monitoring
# ============================================================

import time
import cv2

import rclpy
from rclpy.node import Node

from ultralytics import YOLO


class YOLODetectionNode(Node):

    def __init__(self):

        super().__init__('yolo_detection_node')

        # ----------------------------------------------------
        # 1. Camera Configuration
        # ----------------------------------------------------

        self.camera_id = 0

        self.frame_width = 320
        self.frame_height = 240

        # ----------------------------------------------------
        # 2. YOLO Configuration
        # ----------------------------------------------------

        self.model_path = 'yolo11n.pt'

        self.conf_threshold = 0.40

        self.img_size = 640

        # ----------------------------------------------------
        # 3. Load Pretrained YOLO Model
        # ----------------------------------------------------

        self.get_logger().info(
            'Loading YOLO11 pretrained model...'
        )

        self.model = YOLO(self.model_path)

        self.get_logger().info(
            'YOLO11 Model Loaded Successfully'
        )

        # ----------------------------------------------------
        # 4. Open Webcam
        # ----------------------------------------------------

        self.cap = cv2.VideoCapture(
            self.camera_id,
            cv2.CAP_V4L2
        )

        if not self.cap.isOpened():

            raise RuntimeError(
                'Cannot open webcam'
            )

        # Camera format
        self.cap.set(
            cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*'MJPG')
        )

        # Camera resolution
        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            self.frame_width
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            self.frame_height
        )

        # ----------------------------------------------------
        # 5. FPS Monitoring
        # ----------------------------------------------------

        self.frame_count = 0

        self.start_time = time.perf_counter()

        self.current_fps = 0.0

        # ----------------------------------------------------
        # 6. ROS2 Timer
        # ----------------------------------------------------

        self.timer = self.create_timer(
            0.01,
            self.detect_objects
        )

        # ----------------------------------------------------
        # 7. Startup Information
        # ----------------------------------------------------

        self.get_logger().info(
            '================================'
        )

        self.get_logger().info(
            'PW4 - YOLO Object Detection'
        )

        self.get_logger().info(
            '================================'
        )

        self.get_logger().info(
            f'Model: {self.model_path}'
        )

        self.get_logger().info(
            f'Confidence: {self.conf_threshold}'
        )

        self.get_logger().info(
            'Detection Mode: All Classes'
        )

        self.get_logger().info(
            'Press Q to exit'
        )

    # ========================================================
    # Object Detection
    # ========================================================

    def detect_objects(self):

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
            verbose=False
        )

        result = results[0]

        # ----------------------------------------------------
        # 3. Extract Detection Information
        # ----------------------------------------------------

        detection_count = len(result.boxes)

        # ----------------------------------------------------
        # 4. Draw Bounding Boxes
        # ----------------------------------------------------

        annotated_frame = result.plot()

        # ----------------------------------------------------
        # 5. Calculate Inference Loop FPS
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
        # 6. Display Information
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
            f'Objects: {detection_count}',
            (10, 45),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 255),
            2
        )

        # ----------------------------------------------------
        # 7. Display Video
        # ----------------------------------------------------

        cv2.imshow(
            'PW4 - YOLO General Object Detection',
            annotated_frame
        )

        # Press Q to exit
        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):

            self.get_logger().info(
                'Stopping YOLO Detection'
            )

            rclpy.try_shutdown()

    # ========================================================
    # Cleanup
    # ========================================================

    def destroy_node(self):

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

        node = YOLODetectionNode()

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        if node is not None:

            node.destroy_node()

        rclpy.try_shutdown()


if __name__ == '__main__':

    main()