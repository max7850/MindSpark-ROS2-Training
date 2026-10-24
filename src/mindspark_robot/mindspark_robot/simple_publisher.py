import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SimplePublisher(Node):

    def __init__(self):
        super().__init__('simple_publisher')

        self.publisher = self.create_publisher(
            String, '/message', 10
        )

        self.timer = self.create_timer(
            1.0, self.publish_message
        )

        self.count = 0

    def publish_message(self):

        msg = String()
        msg.data = f'Hello ROS2! Message {self.count}'

        self.publisher.publish(msg)

        self.get_logger().info(f'Publishing: {msg.data}')

        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = SimplePublisher()

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