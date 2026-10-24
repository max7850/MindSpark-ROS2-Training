# MindSpark ROS2 Training Module

**Hands-on ROS 2, computer vision and YOLO object detection training (PW1–PW5)**

MindSpark is an educational robotics package designed to introduce ROS 2 concepts progressively, from nodes and topics to camera-based perception, vision decisions, pretrained YOLO detection and a custom-trained green-ball detector.

> **Project status:** Developed and tested primarily on Ubuntu 24.04 / ROS 2 Jazzy / Python 3.12. A clean-install test on another computer is still recommended before describing the repository as fully reproducible.

## Learning goals

Participants will learn to:

- Create and run ROS 2 Python nodes using `ros2 run`.

- Understand publishers, subscribers, topics and ROS domain configuration.

- Publish images from a USB camera and subscribe to image streams.

- Process camera images using OpenCV and `cv_bridge`.

- Integrate a YOLO object detector into ROS 2.

- Record camera video, prepare an annotated dataset, train and evaluate a custom detector, and deploy it as a ROS 2 node.

## Practical worksheets

| Worksheet | Focus | Representative components | PDF worksheet |
| --- | --- | --- | --- |
| PW1 | ROS 2 foundations | `hello_node`, `simple_publisher`, `simple_subscriber` | [View / Download PW1](docs/worksheets/PW1_ROS2_Fundamentals.pdf) |
| PW2 | ROS 2 communication and basic computer vision | `red_ball_node`, `green_ball_node` | [View / Download PW2](docs/worksheets/PW2_ROS2_Communication.pdf) |
| PW3 | Camera and vision-driven robot integration | `camera_node`, `vision_decision_node`, `esp32_control_node`, `pw3_hardware.launch.py` | [View / Download PW3](docs/worksheets/PW3_ROS2_Hardware_Integration.pdf) |
| PW4 | Pretrained YOLO detection | `yolo_detection_node`, `yolo_sports_ball_node`, `yolo_green_ball_node`, `pw4_yolo_hardware.launch.py` | [View / Download PW4](docs/worksheets/PW4_YOLO_Object_Detection.pdf) |
| PW5 | Custom green-ball YOLO workflow | `video_recorder`, `frame_extractor.py`, `dataset_splitter.py`, `custom_yolo_detection` | [View / Download PW5](docs/worksheets/PW5_Custom_YOLO_Training.pdf) |

Download the PDF worksheets using the links above. The exact practical activities, wiring, topic connections and execution order should be followed from the accompanying PW1–PW5 worksheets. The table above is a guide to package components, not a replacement for those worksheets.

## System requirements

- Ubuntu 24.04 LTS (tested development platform)

- ROS 2 Jazzy

- Python 3.12

- USB camera compatible with OpenCV/V4L2 (for vision practicals)

- Optional ESP32 and motor-controller hardware for physical robot control

- CPU or supported GPU for inference; GPU strongly recommended for custom model training

### ROS 2 dependencies

The ROS 2 package declares `rclpy`, `std_msgs`, `geometry_msgs`, `sensor_msgs` and `cv_bridge` in `package.xml`. A typical Ubuntu 24.04 / Jazzy workstation also needs ROS build tools and corresponding ROS packages installed through `apt` / `rosdep`.

## Repository structure

```text
MindSpark-ROS2-Training/
├── src/
│   └── mindspark_robot/
│       ├── mindspark_robot/         # Python ROS 2 nodes
│       ├── launch/                  # PW3/PW4 launch scripts
│       ├── models/
│       │   └── green_ball_best.pt   # Custom model, subject to distribution rights
│       ├── package.xml
│       ├── setup.py
│       └── setup.cfg
├── docs/
│   └── worksheets/
│       ├── PW1_ROS2_Fundamentals.pdf
│       ├── PW2_ROS2_Communication.pdf
│       ├── PW3_ROS2_Hardware_Integration.pdf
│       ├── PW4_YOLO_Object_Detection.pdf
│       └── PW5_Custom_YOLO_Training.pdf
├── frame_extractor.py
├── dataset_splitter.py
├── requirements.txt
├── yolo_constraints.txt
├── .gitignore
└── README.md
```

Local-only build artifacts, virtual environments, videos, extracted frames, datasets and training outputs are excluded using `.gitignore`.

## Installation (development setup)

### 1. Install ROS 2 Jazzy

Follow the official Ubuntu installation guide: \<https\://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html>.

Install the build tools and required ROS packages through the system package manager; ensure `ros2`, `colcon` and `cv_bridge` work before continuing.

### 2. Clone the repository

```bash
mkdir -p \~/mindspark_ws
cd \~/mindspark_ws
git clone \<YOUR_GITHUB_REPOSITORY_URL> .
```

Replace the placeholder with the published repository URL. Clone into an **empty** directory.

### 3. Create a Python virtual environment

On the tested platform, a virtual environment with access to system ROS packages was used:

```bash
cd \~/mindspark_ws
python3 -m venv --system-site-packages yolo_venv
source /opt/ros/jazzy/setup.bash
source yolo_venv/bin/activate
```

> **Compatibility caution:** ROS `cv_bridge` is built against system-managed libraries. Avoid arbitrarily upgrading NumPy or OpenCV in the venv. The tested environment used NumPy **1.26.4**, OpenCV-Python **4.11.0.86**, Ultralytics **8.4.183**, PyTorch **2.14.1**, Torchvision **0.29.1**. These versions document the development machine; they do not guarantee compatibility with every GPU/driver configuration.

### 4. Install Python dependencies

Install PyTorch/Torchvision from the appropriate CPU/CUDA package source for your device, following \<https\://pytorch.org/get-started/locally/>. Then install the Python application dependencies:

```bash
python -m pip install -r requirements.txt -c yolo_constraints.txt
```

If installation causes conflicts with ROS packages, resolve them before proceeding. The installed PyTorch and Torchvision versions should be checked together, and GPU drivers/CUDA support differ by computer.

### 5. Install ROS package dependencies and build

With ROS 2 sourced, use `rosdep` where available:

```bash
cd \~/mindspark_ws
rosdep install --from-paths src --ignore-src -r -y
python -m colcon build --packages-select mindspark_robot --symlink-install
source install/setup.bash
```

The development machine successfully built with `python -m colcon build` while `yolo_venv` was activated. If the `colcon` Python module is missing in a new virtual environment, install/configure the ROS/colcon build tools first.

## Available executables

The following names are defined in `src/mindspark_robot/setup.py`:

```text
hello_node
camera_node
red_ball_node
green_ball_node
vision_decision_node
esp32_control_node
yolo_detection_node
yolo_sports_ball_node
yolo_green_ball_node
video_recorder
custom_yolo_detection
```

Example ROS commands (after sourcing ROS 2 and the built workspace):

```bash
ros2 run mindspark_robot hello_node
ros2 run mindspark_robot camera_node
ros2 run mindspark_robot custom_yolo_detection
```

Launch files:

```bash
ros2 launch mindspark_robot pw3_hardware.launch.py
ros2 launch mindspark_robot pw4_yolo_hardware.launch.py
```

> Start only the nodes relevant to the worksheet and your connected hardware. The launch files may assume particular topics, devices or serial ports; inspect and adapt their configuration before use.

## Topics and basic verification

Inspect the running graph with:

```bash
ros2 node list
ros2 topic list
ros2 topic info /camera/image_raw
ros2 topic hz /camera/image_raw
```

The camera node was observed publishing `/camera/image_raw`. The custom detector subscribes to this topic and publishes:

- `/custom_yolo/annotated_image` — annotated image (`sensor_msgs/msg/Image`)

- `/custom_yolo/ball_position` — ball location (`geometry_msgs/msg/Point`)

Check your ROS domain on all participating terminals or machines:

```bash
echo "$ROS_DOMAIN_ID"
```

For ROS 2 nodes to communicate across hosts, ensure compatible DDS/network settings and matching ROS domain IDs.

## YOLO inference device: GPU first, CPU fallback

All four YOLO nodes (PW4 general detection, sports-ball detection, green-ball detection, and PW5 custom detection) select **NVIDIA CUDA GPU when PyTorch reports CUDA as available**, otherwise they use **CPU**. No source-code edit is required on a CPU-only machine, provided its Python environment has compatible CPU PyTorch, Ultralytics, and ROS 2 dependencies.

| ROS 2 executable | Camera input | Default inference device |
| --- | --- | --- |
| `yolo_detection_node` | Direct OpenCV webcam | CUDA GPU if available; otherwise CPU |
| `yolo_sports_ball_node` | Direct OpenCV webcam | CUDA GPU if available; otherwise CPU |
| `yolo_green_ball_node` | Subscribes to `/camera/image_raw` | CUDA GPU if available; otherwise CPU |
| `custom_yolo_detection` | Subscribes to `/camera/image_raw` | `device:=auto` (CUDA first, CPU otherwise) |

For PW5, you can explicitly choose a processing device without editing code:

```bash
# Automatic selection (default)
ros2 run mindspark_robot custom_yolo_detection

# Force CPU, even on a machine with CUDA
ros2 run mindspark_robot custom_yolo_detection --ros-args -p device:=cpu

# Request the first CUDA GPU (requires compatible CUDA environment)
ros2 run mindspark_robot custom_yolo_detection --ros-args -p device:=cuda:0
```

**Test evidence:** On the development PC with NVIDIA RTX 2060, PW4 general detection and PW5 custom detection logged CUDA device selection. PW5 also loaded the custom model and started successfully with `device:=cpu`. CPU-only inference on a different computer and clean-clone installation still require independent verification; successful initialization alone does not establish throughput or detection accuracy.

**Important limitations:** This automatic selection applies to *CUDA*, not generic AMD/Intel GPUs, Hailo, or other accelerators. It falls back when CUDA is **unavailable at startup**, but it does **not** automatically recover from a GPU error or out-of-memory failure during loading/inference. CPU execution may be slower, and performance depends on the camera pipeline and hardware.

Build the package using the interpreter that has the YOLO dependencies, as tested with `yolo_venv` activated:

```bash
cd ~/mindspark_ws
source /opt/ros/jazzy/setup.bash
source yolo_venv/bin/activate
python -m colcon build --symlink-install --packages-select mindspark_robot
source install/setup.bash
```

A visible `(yolo_venv)` prompt does not guarantee that a previously generated `ros2 run` executable points to the venv interpreter. If `torch` or `ultralytics` cannot be imported, verify the executable's first line (its *shebang*), e.g. `head -n 1 install/mindspark_robot/lib/mindspark_robot/custom_yolo_detection`, and rebuild with the intended Python interpreter.

## YOLO models

### Pretrained detection (PW4)

The PW4 nodes refer to a model named `yolo11n.pt` in their current code. This model file is **not** included in the repository; it must be obtained separately using the Ultralytics tooling and be available at the location expected by the node. Relative model paths depend on the process working directory unless explicitly configured.

### Custom detection (PW5)

The custom model is expected at:

```text
src/mindspark_robot/models/green_ball_best.pt
```

During the ROS 2 build, `setup.py` installs it in the package share directory. `custom_yolo_detection` resolves the model using `get_package_share_directory('mindspark_robot')` and supports a `model_path` ROS parameter.

Example override:

```bash
ros2 run mindspark_robot custom_yolo_detection --ros-args -p model_path:=/absolute/path/to/best.pt
```

**Validated locally:** package build, installed model path, model loading and `ros2 run` startup. The updated model-install arrangement has not yet been independently tested after a fresh clone.

## Dataset workflow (PW5)

1. Record green-ball videos from the ROS 2 camera stream using `video_recorder`.

2. Extract frames with `frame_extractor.py`.

3. Annotate one class, `green_ball`, in Roboflow or another compatible tool.

4. Split by **recording/session**, rather than random frames from the same recording, to reduce data leakage.

5. Export a compatible Ultralytics dataset and train on an appropriately equipped PC.

6. Evaluate on held-out data and test live detection.

7. Deploy the exported custom `.pt` model through `custom_yolo_detection`.

Raw recordings, annotated datasets and training runs are local development assets and are not automatically included in this repository. Follow the PW5 worksheet for exact dataset naming, training commands and testing criteria.

## Troubleshooting

**`ros2 run` executable not found:** Source `/opt/ros/jazzy/setup.bash` and `install/setup.bash`; rebuild the package and check `setup.py` console-script entries.

**`ModuleNotFoundError: torch` or `ultralytics`:** Ensure the terminal/build uses the intended `yolo_venv`. A new shell does not activate it automatically.

**Custom model not found:** Verify that `src/mindspark_robot/models/green_ball_best.pt` exists, `setup.py` installs `models/*.pt`, and the workspace has been rebuilt and sourced.

**No camera images:** Check camera device access, camera-node output, `/camera/image_raw`, and `ros2 topic hz /camera/image_raw`.

**Nodes cannot communicate:** Check `ROS_DOMAIN_ID`, topic names, QoS compatibility and network configuration.

**NumPy/OpenCV/`cv_bridge` conflicts:** Avoid blind upgrades. Validate the ROS system Python packages and venv package versions together.

## Licensing and redistribution

MindSpark ROS2 Training Module is released under the **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**. See the LICENSE file for the complete license terms. Third-party libraries, pretrained models and custom-trained weights remain subject to their applicable licensing and redistribution requirements.

**Important:** Ultralytics software and model weights can carry separate license and redistribution obligations. Review the applicable license for the pretrained foundation model, custom `green_ball_best.pt`, annotations, training images and videos **before publicly distributing those assets**. The repository license does not override third-party model licenses.

## Credits

Developed for the MindSpark ROS2 hands-on training activities. Maintainer and institutional acknowledgements can be added before public release.

## Contributions

Issues, improvements and teaching adaptations are welcome after repository publication. Please avoid committing credentials, student/personal data, large raw videos, training datasets or machine-specific virtual environments.
