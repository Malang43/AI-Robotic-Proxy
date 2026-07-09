# Team Alpha – Robot & Telepresence  
## Week 1 Documentation: Platform Bring-up & ROS2 Practice

## 1. Objective
The objective of Team Alpha in Week 1 was to prepare the robot development platform for the AI Robotic Proxy project. The assigned tasks included Xavier NX configuration, Ubuntu/JetPack/ROS2 setup, LIDAR verification, SSH configuration, GitHub repository creation, and keyboard teleoperation verification.

## 2. Assigned Tasks and Status

| Task | Status | Remarks |
|---|---|---|
| Configure Xavier NX | Pending | Hardware-dependent task. Kept pending as instructed by teacher. |
| Install Ubuntu | Completed on laptop | Ubuntu 20.04 development environment was prepared for ROS2 practice. |
| Install JetPack | Prepared / Pending | NVIDIA SDK Manager and JetPack workflow explored. Final flashing requires Xavier NX hardware. |
| Install ROS2 | Completed on laptop | ROS2 Foxy was installed and practiced on Ubuntu 20.04. ROS2 Humble will be configured according to final hardware requirement. |
| Verify LIDAR | Procedure prepared / Simulated practice | Real LIDAR verification is pending hardware. Fake `/scan` workflow and RViz2 visualization steps were prepared. |
| Configure Remote SSH | Procedure prepared | SSH setup commands and workflow prepared. Final verification requires Xavier NX IP/network. |
| Create GitHub repository | Completed | Repository structure prepared for code, documentation, screenshots, and setup notes. |
| Verify keyboard teleoperation | Completed in simulation | Turtlesim keyboard teleoperation was successfully tested. |

## 3. Work Completed
During Week 1, Team Alpha focused on preparing the development environment and understanding the robot bring-up workflow before Xavier NX hardware access.

Completed work:
- Ubuntu development environment prepared on laptop.
- ROS2 environment installed and tested.
- ROS2 basic commands practiced, including node list, topic list, topic echo, and package execution.
- Turtlesim used to verify keyboard teleoperation.
- Basic ROS2 concepts studied, including nodes, topics, publishers, subscribers, services, messages, and launch files.
- LIDAR verification workflow studied, including USB detection, serial port checking, `/scan` topic verification, and RViz2 visualization.
- SSH configuration workflow prepared for future Xavier NX remote access.
- GitHub repository structure prepared.
- Digital twin simulation prototypes developed for navigation, obstacle avoidance, path planning, replanning, and dashboard visualization.

## 4. Hardware-Dependent Pending Tasks
Xavier NX configuration, JetPack flashing, real LIDAR verification, and SSH testing are hardware-dependent tasks. These tasks were not finalized during Week 1 because Xavier NX hardware was not available for direct configuration. As instructed by the teacher, these tasks are kept as pending hardware bring-up tasks and will be completed when the Xavier NX board is available.

## 5. Problems Faced and Actions Taken

| Problem | Cause | Action Taken |
|---|---|---|
| Ubuntu and ROS2 version confusion | ROS2 Humble and JetPack versions have OS compatibility differences | Laptop environment was stabilized for ROS2 practice. Final Xavier NX setup will follow hardware/JetPack compatibility. |
| Xavier NX hardware unavailable | Hardware-dependent task | Setup workflow and commands were prepared for future bring-up. |
| Real LIDAR unavailable | Sensor not physically connected yet | LIDAR verification procedure and fake `/scan` practice were prepared. |
| ROS2 beginner difficulty | New concepts such as nodes, topics, and messages | Turtlesim, topic echo, and teleoperation were practiced. |
| Command typing errors | Initial learning stage | Correct ROS2 source and run commands were documented. |

## 6. Digital Twin Exploration
In addition to the official Week 1 tasks, Team Alpha explored digital twin simulation using Python and Pygame. A 2D expo robot navigation prototype and a hospital medicine delivery robot prototype were developed. These simulations helped understand autonomous navigation, path planning, obstacle avoidance, dynamic obstacle handling, emergency stop/resume, and live dashboard visualization.

This work is not a replacement for Xavier NX hardware bring-up, but it supports understanding of the robot navigation and telepresence concept.

## 7. Screenshots / Evidence

Add screenshots in the `screenshots` folder and link them here.

Example:

```markdown
![ROS2 Turtlesim Running](screenshots/turtlesim_running.png)
![Keyboard Teleoperation](screenshots/keyboard_teleop.png)
![Digital Twin Simulation](screenshots/expo_digital_twin.png)
8. Next Week Plan
Configure Xavier NX when hardware is available.
Complete JetPack flashing and target platform setup.
Install required ROS2 version on the robot platform.
Connect and verify LIDAR.
Confirm /scan topic and visualize LaserScan data in RViz2.
Configure SSH from laptop to Xavier NX.
Test keyboard teleoperation on the robot platform.
Update GitHub repository with setup notes and test evidence.
