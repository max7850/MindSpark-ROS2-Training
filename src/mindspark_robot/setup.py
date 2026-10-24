import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'mindspark_robot'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),

    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name]
        ),
        (
            'share/' + package_name,
            ['package.xml']
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')
        ),
        (
            os.path.join('share', package_name, 'models'),
            glob('models/*.pt')
        ),
    ],

    install_requires=['setuptools'],
    zip_safe=True,

    maintainer='ilmi',
    maintainer_email='ilmiariffin@gmail.com',

    description='MindSpark ROS2 Training Package',
    license='AGPL-3.0-or-later',

    tests_require=['pytest'],

    entry_points={
        'console_scripts': [
            'hello_node = mindspark_robot.hello_node:main',
            'camera_node = mindspark_robot.camera_node:main',
            'red_ball_node = mindspark_robot.red_ball_node:main',
            'green_ball_node = mindspark_robot.green_ball_node:main',
            'vision_decision_node = mindspark_robot.vision_decision_node:main',
            'esp32_control_node = mindspark_robot.esp32_control_node:main',
            'yolo_detection_node = mindspark_robot.yolo_detection_node:main',
            'yolo_sports_ball_node = mindspark_robot.yolo_sports_ball_node:main',
            'yolo_green_ball_node = mindspark_robot.yolo_green_ball_node:main',
            'video_recorder = mindspark_robot.video_recorder_node:main',
            'custom_yolo_detection = mindspark_robot.custom_yolo_detection_node:main',
        ],
    },
)