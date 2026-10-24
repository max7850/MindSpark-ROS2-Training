#!/usr/bin/env python3

# ============================================================
# PW3 - ROS2 Vision-Based Hardware Control
# ROS2 Launch File
#
# Package: mindspark_robot
#
# Nodes:
#   1. camera_node
#   2. green_ball_node
#   3. vision_decision_node
#   4. esp32_control_node
#
# Hardware:
#   USB Webcam
#   ESP32 DevKit
#   Red, Yellow, Green LEDs
# ============================================================

from launch import LaunchDescription

from launch_ros.actions import Node


def generate_launch_description():

    # --------------------------------------------------------
    # 1. Camera Node
    # --------------------------------------------------------

    camera_node = Node(
        package='mindspark_robot',
        executable='camera_node',
        name='camera_node',
        output='screen'
    )

    # --------------------------------------------------------
    # 2. Green Ball Detection Node
    # --------------------------------------------------------

    green_ball_node = Node(
        package='mindspark_robot',
        executable='green_ball_node',
        name='green_ball_node',
        output='screen'
    )

    # --------------------------------------------------------
    # 3. Vision Decision Node
    # --------------------------------------------------------

    vision_decision_node = Node(
        package='mindspark_robot',
        executable='vision_decision_node',
        name='vision_decision_node',
        output='screen'
    )

    # --------------------------------------------------------
    # 4. ESP32 Control Node
    # --------------------------------------------------------

    esp32_control_node = Node(
        package='mindspark_robot',
        executable='esp32_control_node',
        name='esp32_control_node',
        output='screen'
    )

    # --------------------------------------------------------
    # Launch Description
    # --------------------------------------------------------

    return LaunchDescription([

        camera_node,
        green_ball_node,
        vision_decision_node,
        esp32_control_node

    ])