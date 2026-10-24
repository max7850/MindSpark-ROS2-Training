#!/usr/bin/env python3

# ============================================================
# PW3 - ROS2 Vision-Based Hardware Control
# Camera Publisher Node - 30 FPS
#
# Package : mindspark_robot
# Node    : camera_node
# Topic   : /camera/image_raw
# Type    : sensor_msgs/msg/Image
#
# Camera Resolution : 320 x 240
# Target FPS        : 30
# Image Encoding    : BGR8
# ============================================================

import time
import cv2

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class CameraNode(Node):

    def __init__(self):

        super().__init__('camera_node')

        # ====================================================
        # 1. Camera Configuration
        # ====================================================

        self.camera_id = 0

        self.frame_width = 320
        self.frame_height = 240
        self.target_fps = 30.0

        # ====================================================
        # 2. ROS2 Publisher
        # ====================================================

        self.publisher = self.create_publisher(
            Image,
            '/camera/image_raw',
            10
        )

        # ====================================================
        # 3. OpenCV Bridge
        # ====================================================

        self.bridge = CvBridge()

        # ====================================================
        # 4. Open Camera
        # ====================================================

        self.cap = cv2.VideoCapture(
            self.camera_id,
            cv2.CAP_V4L2
        )

        if not self.cap.isOpened():

            self.get_logger().error(
                'Cannot open webcam'
            )

            raise RuntimeError(
                'Camera initialization failed'
            )

        # ====================================================
        # 5. Configure Camera
        # ====================================================

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
            self.target_fps
        )

        # ====================================================
        # 6. Read Actual Camera Settings
        # ====================================================

        actual_width = int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        actual_height = int(
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        reported_fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )

        self.get_logger().info(
            '========================================'
        )

        self.get_logger().info(
            'PW3 - ROS2 Camera Publisher'
        )

        self.get_logger().info(
            '========================================'
        )

        self.get_logger().info(
            f'Camera Device: {self.camera_id}'
        )

        self.get_logger().info(
            f'Camera Resolution: '
            f'{actual_width} x {actual_height}'
        )

        self.get_logger().info(
            f'Requested FPS: {self.target_fps:.2f}'
        )

        self.get_logger().info(
            f'Camera Reported FPS: {reported_fps:.2f}'
        )

        # ====================================================
        # 7. FPS Monitoring
        # ====================================================

        self.frame_count = 0

        self.start_time = time.perf_counter()

        self.last_capture_time = None

        # ====================================================
        # 8. ROS2 Timer - 30 Hz
        # ====================================================

        self.timer = self.create_timer(
            1.0 / self.target_fps,
            self.publish_image
        )

        self.get_logger().info(
            'Camera Publisher Started'
        )

        self.get_logger().info(
            'Publishing Target: 30 FPS'
        )

        self.get_logger().info(
            'Topic: /camera/image_raw'
        )

        # ====================================================
        # 9. End Initialization
        # ====================================================

    # ========================================================
    # Publish Camera Image
    # ========================================================

    def publish_image(self):

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
        # 2. Convert OpenCV Frame to ROS2 Image
        # ----------------------------------------------------

        msg = self.bridge.cv2_to_imgmsg(
            frame,
            encoding='bgr8'
        )

        # Assign timestamp
        msg.header.stamp = (
            self.get_clock().now().to_msg()
        )

        # Assign frame ID
        msg.header.frame_id = 'camera'

        # ----------------------------------------------------
        # 3. Publish Image
        # ----------------------------------------------------

        self.publisher.publish(msg)

        # ----------------------------------------------------
        # 4. Update Frame Counter
        # ----------------------------------------------------

        self.frame_count += 1

        # ----------------------------------------------------
        # 5. Calculate Publishing FPS
        # ----------------------------------------------------

        current_time = time.perf_counter()

        elapsed = current_time - self.start_time

        if elapsed >= 5.0:

            actual_fps = (
                self.frame_count / elapsed
            )

            self.get_logger().info(
                f'Camera Publishing FPS: {actual_fps:.2f}'
            )

            # Reset counter
            self.frame_count = 0

            self.start_time = current_time

    # ========================================================
    # Cleanup Camera
    # ========================================================

    def destroy_node(self):

        if self.cap.isOpened():

            self.cap.release()

            self.get_logger().info(
                'Camera Released'
            )

        super().destroy_node()


# ============================================================
# Main Function
# ============================================================

def main(args=None):

    rclpy.init(args=args)

    node = None

    try:

        node = CameraNode()

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    except Exception as e:

        print(f'Camera Node Error: {e}')

    finally:

        if node is not None:

            node.destroy_node()

        if rclpy.ok():

            rclpy.shutdown()


if __name__ == '__main__':

    main()