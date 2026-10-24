#!/usr/bin/env python3

# ============================================================
# PW3 - ROS2 Vision-Based Hardware Control
# ESP32 Control Node
#
# Subscribe:
#   /vision/decision (std_msgs/String)
#
# Serial:
#   Port: /dev/ttyUSB0
#   Baud: 115200
#
# Commands:
#   L = RED LED
#   C = YELLOW LED
#   R = GREEN LED
#   N = ALL LEDs OFF
# ============================================================

import time
import serial

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ESP32ControlNode(Node):

    def __init__(self):

        super().__init__('esp32_control_node')

        # Serial configuration
        self.serial_port = '/dev/ttyUSB0'
        self.baud_rate = 115200

        # Control variables
        self.current_command = 'N'
        self.last_sent_command = None
        self.last_message_time = time.monotonic()

        # Communication timeout
        self.timeout_sec = 2.0

        # Connect to ESP32
        self.esp32 = serial.Serial(
            port=self.serial_port,
            baudrate=self.baud_rate,
            timeout=1,
            write_timeout=1
        )

        # Wait for ESP32 restart
        time.sleep(2)

        self.esp32.reset_input_buffer()

        self.get_logger().info(
            f'ESP32 Connected: {self.serial_port}'
        )

        # ROS2 Subscriber
        self.subscription = self.create_subscription(
            String,
            '/vision/decision',
            self.decision_callback,
            10
        )

        # Timer for communication timeout
        self.timer = self.create_timer(
            0.2,
            self.check_timeout
        )

        # Initialise output
        self.send_command('N')

        self.get_logger().info(
            'ESP32 Control Node Started'
        )

    # --------------------------------------------------------
    # Send command to ESP32
    # --------------------------------------------------------

    def send_command(self, command):

        try:

            self.esp32.write(
                command.encode('utf-8')
            )

            self.esp32.flush()

            # Log only when command changes
            if command != self.last_sent_command:

                self.get_logger().info(
                    f'ESP32 Command: {command}'
                )

            self.last_sent_command = command

        except serial.SerialException as e:

            self.get_logger().error(
                f'Serial Error: {e}'
            )

    # --------------------------------------------------------
    # Receive ROS2 decision
    # --------------------------------------------------------

    def decision_callback(self, msg):

        command = msg.data.strip().upper()

        if command not in ['L', 'C', 'R', 'N']:

            self.get_logger().warning(
                f'Invalid command: {command}'
            )

            return

        self.last_message_time = time.monotonic()
        self.current_command = command

        # Send only when command changes
        if command != self.last_sent_command:

            self.send_command(command)

    # --------------------------------------------------------
    # Check communication timeout
    # --------------------------------------------------------

    def check_timeout(self):

        elapsed = (
            time.monotonic()
            - self.last_message_time
        )

        if elapsed > self.timeout_sec:

            self.current_command = 'N'

            if self.last_sent_command != 'N':

                self.get_logger().warning(
                    'ROS2 Communication Timeout'
                )

                self.send_command('N')

    # --------------------------------------------------------
    # Shutdown
    # --------------------------------------------------------

    def shutdown(self):

        if self.esp32.is_open:

            try:
                self.esp32.write(b'N')
                self.esp32.flush()

            except serial.SerialException:
                pass

            self.esp32.close()


def main(args=None):

    rclpy.init(args=args)

    node = None

    try:

        node = ESP32ControlNode()
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    except serial.SerialException as e:
        print(f'ESP32 Connection Error: {e}')

    finally:

        if node is not None:
            node.shutdown()
            node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()