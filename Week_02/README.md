
# Week 02 – Team Alpha Progress

## Project
AI-Powered Robotic Proxy for Remote Business Presence in Expos

## Team
Team Alpha – Robotics / Telepresence

## Contributor
M Farhat Mehdi

---

## Week 2 Current Status

This README documents the Week 2 progress completed so far. At this stage, software-based ROS2 tasks have been completed using Ubuntu 20.04 and ROS2 Foxy on the laptop.

Hardware-dependent tasks will be updated later if the Jetson board, LIDAR, robot base, or indigenous robot platform becomes available during this week.

---

## Software Work Completed

### 1. ROS2 Workspace and Package Setup

A ROS2 workspace was created for Week 2 practice.

Workspace:

```bash
Team_Alpha_ROS2_Software/ros2_workspace
````

Package:

```bash
week2_ros2_practice
```

The package was built using:

```bash
colcon build
```

---

### 2. Simple ROS2 Node

A simple ROS2 node was created to understand the basic structure of a ROS2 program.

File:

```bash
simple_node.py
```

Run command:

```bash
ros2 run week2_ros2_practice simple_node
```

Purpose:

* Practiced creating a basic ROS2 node
* Used a timer callback
* Printed periodic status messages

---

### 3. Topic Publisher and Subscriber

A topic publisher and subscriber were created to practice ROS2 topic communication.

Files:

```bash
topic_publisher.py
topic_subscriber.py
```

Topic:

```bash
/week2_status
```

Run commands:

```bash
ros2 run week2_ros2_practice topic_publisher
ros2 run week2_ros2_practice topic_subscriber
```

Purpose:

* Publisher sends messages
* Subscriber receives messages
* Practiced basic ROS2 topic communication

---

### 4. Velocity Command Publisher using Turtlesim

A velocity publisher was created to send movement commands to turtlesim.

File:

```bash
velocity_publisher.py
```

Topic:

```bash
/turtle1/cmd_vel
```

Run command:

```bash
ros2 run week2_ros2_practice velocity_publisher
```

Purpose:

* Practiced velocity command publishing
* Sent linear and angular velocity commands
* Controlled turtlesim movement automatically

Relevance to project:

* Real robot movement will later use velocity commands such as `/cmd_vel`

---

### 5. Pose Subscriber using Turtlesim

A pose subscriber was created to read turtle position and orientation.

File:

```bash
pose_subscriber.py
```

Topic:

```bash
/turtle1/pose
```

Run command:

```bash
ros2 run week2_ros2_practice pose_subscriber
```

Purpose:

* Practiced subscribing to position data
* Observed x, y, theta, linear velocity, and angular velocity

Relevance to project:

* This helps understand odometry-like data before using real `/odom`

---

### 6. ROS2 Service Server and Client

A service server and client were created using the AddTwoInts service.

Files:

```bash
service_server.py
service_client.py
```

Service:

```bash
/add_two_ints
```

Run commands:

```bash
ros2 run week2_ros2_practice service_server
ros2 run week2_ros2_practice service_client 5 7
```

Purpose:

* Practiced request-response communication
* Client sends request
* Server processes request and returns result

Relevance to project:

* Services can later be used for robot commands such as start, stop, reset, or status check

---

### 7. ROS2 Parameter Node

A parameter node was created to practice changing node settings from the terminal.

File:

```bash
parameter_node.py
```

Run command:

```bash
ros2 run week2_ros2_practice parameter_node
```

Run with custom parameters:

```bash
ros2 run week2_ros2_practice parameter_node --ros-args -p robot_name:=expo_robot -p robot_speed:=1.2
```

Parameters:

```bash
robot_name
robot_speed
```

Purpose:

* Practiced declaring ROS2 parameters
* Changed node settings without editing code

Relevance to project:

* Parameters can later be used for robot speed, robot name, camera settings, and sensor settings

---

### 8. ROS Bag Recording and Replay

ROS bag recording and replay were practiced using turtlesim topics.

Recorded topics:

```bash
/turtle1/cmd_vel
/turtle1/pose
```

Bag folder:

```bash
Team_Alpha_ROS2_Software/rosbag_practice/bags/week2_turtlesim_bag
```

Record command:

```bash
ros2 bag record /turtle1/cmd_vel /turtle1/pose -o week2_turtlesim_bag
```

Bag info command:

```bash
ros2 bag info week2_turtlesim_bag
```

Replay command:

```bash
ros2 bag play week2_turtlesim_bag
```

Purpose:

* Practiced recording ROS2 topic data
* Practiced replaying recorded ROS2 topic data
* Verified movement data using turtlesim

Relevance to project:

* ROS bags will later be used to record robot topics such as `/cmd_vel`, `/odom`, `/scan`, and other sensor data

---

### 9. ROS2 Action Server and Client

An action server and client were created using the Fibonacci action example.

Files:

```bash
action_server.py
action_client.py
```

Action:

```bash
/fibonacci
```

Run commands:

```bash
ros2 run week2_ros2_practice action_server
ros2 run week2_ros2_practice action_client 6
```

Purpose:

* Practiced ROS2 action communication
* Client sends a goal
* Server gives feedback
* Server returns final result

Relevance to project:

* Actions are useful for long-running robot tasks such as navigation, mapping, or moving to a target location

---

## Completed Software Task Summary

| Task                         | Status    |
| ---------------------------- | --------- |
| ROS2 workspace setup         | Completed |
| ROS2 package creation        | Completed |
| Simple ROS2 node             | Completed |
| Topic publisher/subscriber   | Completed |
| Velocity command publisher   | Completed |
| Pose subscriber              | Completed |
| Service server/client        | Completed |
| Parameter node               | Completed |
| ROS bag recording and replay | Completed |
| Action server/client         | Completed |
---

## Real LIDAR Hardware Verification

### RPLIDAR S2M1R2 Test

The RPLIDAR S2M1R2 was connected to the laptop using the SLAMTEC USB adapter. The device was successfully detected as a serial USB device.

Detected device:

```bash
/dev/ttyUSB0
---
cd ~/AI-Robotic-Proxy/Week_02
nano README.md
```


## Real LIDAR Hardware Verification

### RPLIDAR S2M1R2 Test

The RPLIDAR S2M1R2 was connected to the laptop using the SLAMTEC USB adapter. The device was successfully detected as a serial USB device.

Detected device:

```bash
/dev/ttyUSB0
````

Permission command:

```bash
sudo chmod 666 /dev/ttyUSB0
```

The SLAMTEC ROS2 driver was launched successfully using:

```bash
cd ~/AI-Robotic-Proxy/Week_02/Team_Alpha_LIDAR_Hardware/sllidar_ws
source /opt/ros/foxy/setup.bash
source install/setup.bash
ros2 launch sllidar_ros2 view_sllidar_s2_launch.py
```

The LIDAR successfully published scan data on:

```bash
/scan
```

The scan data was checked using:

```bash
ros2 topic list
ros2 topic echo /scan
ros2 topic hz /scan
```

RViz2 was used to visualize the real LaserScan data.

RViz2 settings:

```bash
Fixed Frame: laser
LaserScan Topic: /scan
```

Evidence files:

```bash
Team_Alpha_LIDAR_Hardware/screenshots/rviz2_rplidar_scan.png
Team_Alpha_LIDAR_Hardware/commands/scan_frequency.txt
Team_Alpha_LIDAR_Hardware/commands/ros2_topic_list.txt
```

Status:

```text
RPLIDAR S2M1R2 detection, /scan topic publishing, frequency check, and RViz2 visualization were completed successfully.


## Hardware Tasks Not Completed Yet

The following tasks are not completed yet because the physical hardware is not currently available:

| Hardware Task                          | Status  |
| -------------------------------------- | ------- |
| Jetson Nano/Xavier NX verification     | Pending |
| SSH connection to robot platform       | Pending |
| Real LIDAR integration                 | Pending |
| Real `/scan` topic                     | Pending |
| RViz2 visualization of real LIDAR data | Pending |
| Real `/odom` from robot base           | Pending |
| SLAM Toolbox occupancy grid mapping    | Pending |
| Indigenous robot platform testing      | Pending |



