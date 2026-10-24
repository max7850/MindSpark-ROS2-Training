import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge

import cv2
import numpy as np


class RedBallNode(Node):

    def __init__(self):
        super().__init__('red_ball_node')

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
            '/red_ball',
            10
        )

        self.get_logger().info('Red Ball Detection Started')

    def image_callback(self, msg):

        # Convert ROS2 Image to OpenCV
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        # Convert BGR to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Red HSV ranges
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])

        lower_red2 = np.array([170, 100, 100])
        upper_red2 = np.array([179, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask1 + mask2

        # Find contours
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        result = String()
        result.data = 'NOT DETECTED'

        if contours:

            largest = max(contours, key=cv2.contourArea)

            if cv2.contourArea(largest) > 200:

                x, y, w, h = cv2.boundingRect(largest)

                cx = x + w // 2
                cy = y + h // 2

                result.data = f'DETECTED: x={cx}, y={cy}'

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    2
                )

                cv2.circle(
                    frame,
                    (cx, cy),
                    4,
                    (255, 255, 255),
                    -1
                )

        # Publish detection result
        self.publisher.publish(result)

        # Display detection
        cv2.imshow('Red Ball Detection', frame)
        cv2.waitKey(1)

    def destroy_node(self):

        cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)
    node = RedBallNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()