#!/usr/bin/env python3

from pathlib import Path
import shutil
from collections import defaultdict

# -----------------------------------
# Configuration
# -----------------------------------

BASE = Path.home() / "mindspark_ws/dataset/training"

SOURCE = BASE / "green_ball_v1"
DEST = BASE / "green_ball_v2"

# Group-based split
SPLIT_MAP = {
    "green_ball_20261023_152117": "train",
    "green_ball_20261023_152415": "train",
    "green_ball_20261023_152547": "train",
    "green_ball_20261023_152717": "valid",
    "green_ball_20261023_152916": "test",
}

# -----------------------------------
# Create Output Directories
# -----------------------------------

for split in ["train", "valid", "test"]:

    (DEST / split / "images").mkdir(
        parents=True,
        exist_ok=True
    )

    (DEST / split / "labels").mkdir(
        parents=True,
        exist_ok=True
    )

# -----------------------------------
# Copy Images and Labels
# -----------------------------------

counts = defaultdict(int)

for original_split in ["train", "valid", "test"]:

    image_dir = SOURCE / original_split / "images"
    label_dir = SOURCE / original_split / "labels"

    for image in image_dir.iterdir():

        if image.suffix.lower() not in [
            ".jpg", ".jpeg", ".png"
        ]:
            continue

        # Identify recording session
        session = image.name.split("_frame_")[0]

        if session not in SPLIT_MAP:

            print(f"WARNING: Unknown session: {image.name}")
            continue

        new_split = SPLIT_MAP[session]

        # Copy image
        shutil.copy2(
            image,
            DEST / new_split / "images" / image.name
        )

        # Copy matching label
        label = label_dir / (image.stem + ".txt")

        if label.exists():

            shutil.copy2(
                label,
                DEST / new_split / "labels" / label.name
            )

        counts[new_split] += 1

# -----------------------------------
# Create data.yaml
# -----------------------------------

yaml_content = f"""path: {DEST}
train: train/images
val: valid/images
test: test/images

nc: 1
names: ['green_ball']
"""

(DEST / "data.yaml").write_text(yaml_content)

# -----------------------------------
# Summary
# -----------------------------------

print("\n=================================")
print(" DATASET SPLITTING COMPLETED")
print("=================================")

total = sum(counts.values())

for split in ["train", "valid", "test"]:

    count = counts[split]

    percentage = (
        count / total * 100
        if total > 0 else 0
    )

    print(
        f"{split}: {count} images "
        f"({percentage:.1f}%)"
    )

print(f"\nTotal: {total} images")

print(f"\nOutput: {DEST}")