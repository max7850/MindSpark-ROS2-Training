#!/usr/bin/env python3

import os
import time

import cv2
import rclpy

from ament_index_python.packages import get_package_share_directory

from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image
from geometry_msgs.msg import Point

from cv_bridge import CvBridge
from ultralytics import YOLO


class CustomYOLODetectionNode(Node):

    def __init__(self):

        super().__init__('custom_yolo_detection')

        # -----------------------------------
        # Parameters
        # -----------------------------------

        # Locate model from the installed ROS2 package
        package_share = get_package_share_directory('mindspark_robot')

        default_model = os.path.join(
            package_share,
            'models',
            'green_ball_best.pt'
        )

        self.declare_parameter('model_path', default_model)
        self.declare_parameter('confidence', 0.5)
        self.declare_parameter('device', '0')

        self.model_path = self.get_parameter('model_path').value
        self.confidence = self.get_parameter('confidence').value
        self.device = self.get_parameter('device').value

        # -----------------------------------
        # Load Custom YOLO Model
        # -----------------------------------

        if not os.path.isfile(self.model_path):
            raise FileNotFoundError(
                f'Model not found: {self.model_path}'
            )

        self.get_logger().info(
            f'Loading custom YOLO model: {self.model_path}'
        )

        self.model = YOLO(self.model_path)

        self.get_logger().info(
            'Custom YOLO model loaded successfully'
        )

        # -----------------------------------
        # CV Bridge
        # -----------------------------------

        self.bridge = CvBridge()

        # -----------------------------------
        # ROS2 Subscriber
        # -----------------------------------

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            qos_profile_sensor_data
        )

        # -----------------------------------
        # ROS2 Publishers
        # -----------------------------------

        # RELIABLE publisher for image viewers
        self.image_publisher = self.create_publisher(
            Image,
            '/custom_yolo/annotated_image',
            10
        )

        self.position_publisher = self.create_publisher(
            Point,
            '/custom_yolo/ball_position',
            10
        )

        # -----------------------------------
        # Display Configuration
        # -----------------------------------

        self.window_name = 'ROS2 Custom YOLO Detection'

        cv2.namedWindow(
            self.window_name,
            cv2.WINDOW_NORMAL
        )

        self.quit_requested = False

        # -----------------------------------
        # FPS Variables
        # -----------------------------------

        self.previous_time = time.perf_counter()
        self.fps = 0.0
        self.frame_count = 0

        self.get_logger().info(
            'Custom YOLO Detection Node Started'
        )

        self.get_logger().info(
            'Waiting for camera images...'
        )

        self.get_logger().info(
            'Press Q to Quit'
        )

    # -----------------------------------
    # Image Callback
    # -----------------------------------

    def image_callback(self, msg):

        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

        except Exception as e:
            self.get_logger().error(
                f'Image conversion error: {e}'
            )
            return

        # -----------------------------------
        # YOLO Inference
        # -----------------------------------

        results = self.model.predict(
            source=frame,
            conf=self.confidence,
            device=self.device,
            verbose=False
        )

        result = results[0]

        # Draw bounding boxes and confidence
        annotated_frame = result.plot()

        # -----------------------------------
        # Process Detection
        # -----------------------------------

        detections = []

        for box in result.boxes:

            class_id = int(box.cls[0].item())

            confidence = float(
                box.conf[0].item()
            )

            class_name = self.model.names[class_id]

            if class_name != 'green_ball':
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            center_x = (x1 + x2) / 2.0
            center_y = (y1 + y2) / 2.0

            detections.append(
                (
                    confidence,
                    center_x,
                    center_y
                )
            )

        # -----------------------------------
        # Publish Ball Position
        # -----------------------------------

        # Highest-confidence detection only
        if detections:

            best_detection = max(
                detections,
                key=lambda detection: detection[0]
            )

            confidence, center_x, center_y = best_detection

            position_msg = Point()

            position_msg.x = center_x
            position_msg.y = center_y

            # z stores detection confidence
            position_msg.z = confidence

            self.position_publisher.publish(
                position_msg
            )

            # Draw selected ball centre
            cv2.circle(
                annotated_frame,
                (
                    int(center_x),
                    int(center_y)
                ),
                5,
                (255, 0, 255),
                -1
            )

        # -----------------------------------
        # Calculate Processing FPS
        # -----------------------------------

        current_time = time.perf_counter()

        elapsed_time = (
            current_time - self.previous_time
        )

        if elapsed_time > 0:
            self.fps = 1.0 / elapsed_time

        self.previous_time = current_time

        self.frame_count += 1

        # -----------------------------------
        # Display Information
        # -----------------------------------

        cv2.putText(
            annotated_frame,
            f'Custom YOLO11 | FPS: {self.fps:.1f}',
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )

        cv2.putText(
            annotated_frame,
            f'Detections: {len(detections)}',
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 255),
            2
        )

        # -----------------------------------
        # Publish Annotated Image
        # -----------------------------------

        image_msg = self.bridge.cv2_to_imgmsg(
            annotated_frame,
            encoding='bgr8'
        )

        image_msg.header = msg.header

        self.image_publisher.publish(
            image_msg
        )

        # -----------------------------------
        # Live Detection Display
        # -----------------------------------

        cv2.imshow(
            self.window_name,
            annotated_frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            self.get_logger().info(
                'Q pressed. Shutting down...'
            )
            self.quit_requested = True


# -----------------------------------
# Main
# -----------------------------------

def main(args=None):

    rclpy.init(args=args)

    node = None

    try:

        node = CustomYOLODetectionNode()

        # Process ROS2 callbacks and GUI events
        while rclpy.ok() and not node.quit_requested:
            rclpy.spin_once(
                node,
                timeout_sec=0.1
            )

    except KeyboardInterrupt:
        pass

    finally:

        if node is not None:
            node.destroy_node()

        cv2.destroyAllWindows()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()