#!/usr/bin/env python3

import cv2
from pathlib import Path


# -----------------------------------
# Configuration
# -----------------------------------

BASE_DIR = Path.home() / "mindspark_ws" / "dataset"

VIDEO_DIR = BASE_DIR / "videos"
IMAGE_DIR = BASE_DIR / "images"

# Approximate actual camera publishing FPS
SOURCE_FPS = 7.68

# Desired extraction rate
TARGET_FPS = 2.0

IMAGE_QUALITY = 95


# -----------------------------------
# Extract Frames
# -----------------------------------

def extract_frames(video_path):

    print(f"\nProcessing: {video_path.name}")

    video_name = video_path.stem

    output_dir = IMAGE_DIR / video_name
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        print("ERROR: Cannot open video.")
        return

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    encoded_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"Total frames : {total_frames}")
    print(f"Encoded FPS  : {encoded_fps:.2f}")
    print(f"Source FPS   : {SOURCE_FPS:.2f} (estimated)")
    print(f"Target FPS   : {TARGET_FPS:.2f}")

    frame_index = 0
    saved_count = 0

    next_sample_time = 0.0
    sample_interval = 1.0 / TARGET_FPS

    while True:

        ret, frame = cap.read()

        if not ret:
            break

        # Estimate capture time using source FPS
        frame_time = frame_index / SOURCE_FPS

        if frame_time >= next_sample_time:

            filename = (
                f"{video_name}_frame_{frame_index:06d}.jpg"
            )

            output_path = output_dir / filename

            success = cv2.imwrite(
                str(output_path),
                frame,
                [cv2.IMWRITE_JPEG_QUALITY, IMAGE_QUALITY]
            )

            if success:
                saved_count += 1

            next_sample_time += sample_interval

        frame_index += 1

    cap.release()

    print(f"Frames read  : {frame_index}")
    print(f"Images saved : {saved_count}")
    print(f"Output       : {output_dir}")


# -----------------------------------
# Main Program
# -----------------------------------

def main():

    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    videos = sorted(VIDEO_DIR.glob("*.mp4"))

    if not videos:
        print("No MP4 files found.")
        return

    print("====================================")
    print(" PW5 - VIDEO FRAME EXTRACTION")
    print("====================================")

    print(f"Videos found: {len(videos)}")

    for video in videos:
        extract_frames(video)

    print("\n====================================")
    print(" FRAME EXTRACTION COMPLETED")
    print("====================================")


if __name__ == "__main__":
    main()