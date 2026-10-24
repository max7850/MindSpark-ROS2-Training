#!/usr/bin/env python3

# ============================================================
# PW4 - YOLO Vision-Based Hardware Control
# ROS2 Launch File
#
# Package: mindspark_robot
#
# Nodes:
#   1. camera_node
#   2. yolo_green_ball_node (YOLO Virtual Environment)
#   3. vision_decision_node (Topic Remapping)
#   4. esp32_control_node
#
# ============================================================

import os

from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():

    # --------------------------------------------------------
    # 1. YOLO Virtual Environment Configuration
    # --------------------------------------------------------

    home = os.path.expanduser('~')

    yolo_python = os.path.join(
        home,
        'mindspark_ws',
        'yolo_venv',
        'bin',
        'python3'
    )

    yolo_executable = os.path.join(
        home,
        'mindspark_ws',
        'install',
        'mindspark_robot',
        'lib',
        'mindspark_robot',
        'yolo_green_ball_node'
    )

    # --------------------------------------------------------
    # 2. Camera Node
    # --------------------------------------------------------

    camera_node = Node(
        package='mindspark_robot',
        executable='camera_node',
        name='camera_node',
        output='screen'
    )

    # --------------------------------------------------------
    # 3. YOLO Green Ball Node
    # --------------------------------------------------------

    yolo_green_ball_node = ExecuteProcess(
        cmd=[
            yolo_python,
            yolo_executable
        ],
        output='screen'
    )

    # --------------------------------------------------------
    # 4. Vision Decision Node
    # --------------------------------------------------------

    vision_decision_node = Node(
        package='mindspark_robot',
        executable='vision_decision_node',
        name='vision_decision_node',
        output='screen',

        remappings=[
            ('/green_ball', '/yolo/green_ball')
        ]
    )

    # --------------------------------------------------------
    # 5. ESP32 Control Node
    # --------------------------------------------------------

    esp32_control_node = Node(
        package='mindspark_robot',
        executable='esp32_control_node',
        name='esp32_control_node',
        output='screen'
    )

    # --------------------------------------------------------
    # 6. Launch All Nodes
    # --------------------------------------------------------

    return LaunchDescription([
        camera_node,
        yolo_green_ball_node,
        vision_decision_node,
        esp32_control_node
    ])