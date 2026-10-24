#!/usr/bin/env python3

# ============================================================
# PW3 - ROS2 Vision-Based Hardware Control
# Vision Decision Node
#
# Subscribe:
#   /green_ball       (std_msgs/String)
#
# Publish:
#   /vision/decision  (std_msgs/String)
#
# Decision:
#   L = LEFT
#   C = CENTER
#   R = RIGHT
#   N = NOT DETECTED
#
# Camera Resolution: 320 x 240
# Publishing Frequency: 5 Hz
# Detection Timeout: 1 second
# ============================================================

import re
import time

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class VisionDecisionNode(Node):

    def __init__(self):

        super().__init__('vision_decision_node')

        # ----------------------------------------------------
        # 1. Camera Configuration
        # ----------------------------------------------------

        self.frame_width = 320

        # Divide camera frame into 3 regions
        self.left_boundary = self.frame_width // 3
        self.right_boundary = (self.frame_width * 2) // 3

        # ----------------------------------------------------
        # 2. Decision Variables
        # ----------------------------------------------------

        # Initial decision: No ball detected
        self.current_decision = 'N'

        # Store previous decision for logging
        self.last_logged_decision = None

        # Record time of latest detection message
        self.last_message_time = time.monotonic()

        # Detection timeout
        self.timeout_sec = 1.0

        # ----------------------------------------------------
        # 3. ROS2 Subscriber
        # ----------------------------------------------------

        self.subscription = self.create_subscription(
            String,
            '/green_ball',
            self.ball_callback,
            10
        )

        # ----------------------------------------------------
        # 4. ROS2 Publisher
        # ----------------------------------------------------

        self.publisher = self.create_publisher(
            String,
            '/vision/decision',
            10
        )

        # ----------------------------------------------------
        # 5. ROS2 Timer
        # ----------------------------------------------------

        # Publish decision continuously at 5 Hz
        self.publish_timer = self.create_timer(
            0.2,
            self.publish_current_decision
        )

        # ----------------------------------------------------
        # 6. Startup Information
        # ----------------------------------------------------

        self.get_logger().info(
            'Vision Decision Node Started'
        )

        self.get_logger().info(
            'Camera Resolution: 320 x 240'
        )

        self.get_logger().info(
            'Decision Publishing Frequency: 5 Hz'
        )

        self.get_logger().info(
            'Waiting for green ball detection...'
        )

    # ========================================================
    # Receive Green Ball Detection
    # ========================================================

    def ball_callback(self, msg):

        # Record latest message time
        self.last_message_time = time.monotonic()

        data = msg.data.strip()

        # ----------------------------------------------------
        # Case 1: Ball not detected
        # ----------------------------------------------------

        if data.startswith('NOT DETECTED'):

            self.current_decision = 'N'
            return

        # ----------------------------------------------------
        # Case 2: Validate detection message
        # ----------------------------------------------------

        if not data.startswith('DETECTED:'):

            self.get_logger().warning(
                f'Unknown detection message: {data}'
            )

            self.current_decision = 'N'
            return

        # ----------------------------------------------------
        # Case 3: Extract X coordinate
        # ----------------------------------------------------

        match = re.search(
            r'\bx\s*=\s*(\d+)',
            data
        )

        if match is None:

            self.get_logger().warning(
                f'Invalid detection message: {data}'
            )

            self.current_decision = 'N'
            return

        x = int(match.group(1))

        # ----------------------------------------------------
        # Case 4: Validate X coordinate
        # ----------------------------------------------------

        if x < 0 or x >= self.frame_width:

            self.get_logger().warning(
                f'X coordinate out of range: {x}'
            )

            self.current_decision = 'N'
            return

        # ----------------------------------------------------
        # Case 5: Determine ball position
        # ----------------------------------------------------

        if x < self.left_boundary:

            self.current_decision = 'L'

        elif x < self.right_boundary:

            self.current_decision = 'C'

        else:

            self.current_decision = 'R'

    # ========================================================
    # Publish Vision Decision at 5 Hz
    # ========================================================

    def publish_current_decision(self):

        # ----------------------------------------------------
        # 1. Check detection timeout
        # ----------------------------------------------------

        elapsed = (
            time.monotonic()
            - self.last_message_time
        )

        if elapsed > self.timeout_sec:

            self.current_decision = 'N'

        # ----------------------------------------------------
        # 2. Publish current decision
        # ----------------------------------------------------

        msg = String()
        msg.data = self.current_decision

        self.publisher.publish(msg)

        # ----------------------------------------------------
        # 3. Log only when decision changes
        # ----------------------------------------------------

        if self.current_decision != self.last_logged_decision:

            self.get_logger().info(
                f'Vision Decision: {self.current_decision}'
            )

            self.last_logged_decision = self.current_decision


# ============================================================
# Main Function
# ============================================================

def main(args=None):

    rclpy.init(args=args)

    node = VisionDecisionNode()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:

        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()