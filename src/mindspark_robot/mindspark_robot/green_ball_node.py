import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2
import numpy as np


class GreenBallNode(Node):

    def __init__(self):
        super().__init__('green_ball_node')

        self.bridge = CvBridge()

        # Image Subscriber
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        # Detection Publisher
        self.publisher = self.create_publisher(
            String,
            '/green_ball',
            10
        )

        self.get_logger().info(
            'Green Ball Detection Started'
        )

    def image_callback(self, msg):

        # Convert ROS2 Image to OpenCV image
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        # Convert BGR to HSV
        hsv = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2HSV
        )

        # Green HSV range
        lower_green = np.array([35, 70, 70])
        upper_green = np.array([85, 255, 255])

        # Create green colour mask
        mask = cv2.inRange(
            hsv,
            lower_green,
            upper_green
        )

        # Find contours
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Default detection result
        result = String()
        result.data = 'NOT DETECTED'

        if contours:

            # Find largest contour
            largest = max(
                contours,
                key=cv2.contourArea
            )

            # Filter small objects
            if cv2.contourArea(largest) > 200:

                # Bounding box
                x, y, w, h = cv2.boundingRect(largest)

                # Calculate centroid
                cx = x + w // 2
                cy = y + h // 2

                # Detection message
                result.data = f'DETECTED: x={cx}, y={cy}'

                # Draw green bounding box
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                # Draw centroid
                cv2.circle(
                    frame,
                    (cx, cy),
                    4,
                    (255, 255, 255),
                    -1
                )

                # Display detection coordinates
                cv2.putText(
                    frame,
                    f'GREEN BALL ({cx}, {cy})',
                    (x, max(y - 10, 15)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        # Publish detection result
        self.publisher.publish(result)

        # Display video
        cv2.imshow('Green Ball Detection', frame)
        cv2.waitKey(1)

    def destroy_node(self):

        cv2.destroyAllWindows()
        return super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = None

    try:
        node = GreenBallNode()
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