#!/usr/bin/env python3

import os
import cv2

from datetime import datetime

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class VideoRecorderNode(Node):

    def __init__(self):

        super().__init__('video_recorder')

        # -----------------------------------
        # ROS2 Subscriber
        # -----------------------------------

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10
        )

        self.bridge = CvBridge()

        # -----------------------------------
        # Recording Configuration
        # -----------------------------------

        self.output_dir = os.path.expanduser(
            '~/mindspark_ws/dataset/videos'
        )

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )

        self.recording = False
        self.video_writer = None

        self.frame_count = 0
        self.record_fps = 30.0

        self.get_logger().info(
            'Video Recorder Node Started'
        )

        self.get_logger().info(
            'Press R to Record, S to Stop, Q to Quit'
        )

    # -----------------------------------
    # Start Recording
    # -----------------------------------

    def start_recording(self, frame):

        if self.recording:
            return

        timestamp = datetime.now().strftime(
            '%Y%m%d_%H%M%S'
        )

        filename = f'green_ball_{timestamp}.mp4'

        filepath = os.path.join(
            self.output_dir,
            filename
        )

        height, width = frame.shape[:2]

        fourcc = cv2.VideoWriter_fourcc(
            *'mp4v'
        )

        self.video_writer = cv2.VideoWriter(
            filepath,
            fourcc,
            self.record_fps,
            (width, height)
        )

        if not self.video_writer.isOpened():

            self.get_logger().error(
                'Failed to create video file'
            )

            self.video_writer.release()
            self.video_writer = None
            return

        self.recording = True
        self.frame_count = 0

        self.get_logger().info(
            f'Recording started: {filepath}'
        )

    # -----------------------------------
    # Stop Recording
    # -----------------------------------

    def stop_recording(self):

        if not self.recording:
            return

        self.recording = False

        if self.video_writer is not None:

            self.video_writer.release()
            self.video_writer = None

        self.get_logger().info(
            f'Recording stopped. Frames saved: {self.frame_count}'
        )

    # -----------------------------------
    # Camera Callback
    # -----------------------------------

    def image_callback(self, msg):

        try:

            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding='bgr8'
            )

        except Exception as e:

            self.get_logger().error(
                f'Image conversion failed: {e}'
            )

            return

        # -----------------------------------
        # Save Video Frames
        # -----------------------------------

        if self.recording:

            self.video_writer.write(frame)

            self.frame_count += 1

        # -----------------------------------
        # Display Information
        # -----------------------------------

        display_frame = frame.copy()

        if self.recording:

            status = 'REC'

            color = (0, 0, 255)

        else:

            status = 'STANDBY'

            color = (0, 255, 0)

        cv2.putText(
            display_frame,
            status,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2
        )

        cv2.putText(
            display_frame,
            f'Frames: {self.frame_count}',
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            'ROS2 Video Recorder',
            display_frame
        )

        key = cv2.waitKey(1) & 0xFF

        # R = Record
        if key == ord('r'):

            self.start_recording(frame)

        # S = Stop
        elif key == ord('s'):

            self.stop_recording()

        # Q = Quit
        elif key == ord('q'):

            self.stop_recording()

            rclpy.shutdown()


def main(args=None):

    rclpy.init(args=args)

    node = VideoRecorderNode()

    try:

        rclpy.spin(node)

    except KeyboardInterrupt:

        pass

    finally:

        node.stop_recording()

        node.destroy_node()

        cv2.destroyAllWindows()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()