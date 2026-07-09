# AI Robotic Proxy

## Project Title
AI-Powered Robotic Proxy for Remote Business Presence in Expos

## Project Overview
This project aims to develop an AI-powered robotic proxy that can represent a remote business user in an expo environment. The robot is expected to navigate inside expo spaces, support telepresence, avoid obstacles, and provide remote interaction using AI and backend services.

## Team Structure

### Team Alpha – Robot & Telepresence
Team Alpha focuses on:
- Xavier NX platform bring-up
- Ubuntu, JetPack, and ROS2 setup
- LIDAR verification
- Remote SSH configuration
- Keyboard teleoperation
- Robot navigation and digital twin exploration

### Team Beta – AI Stack & Backend
Team Beta focuses on:
- GPU workstation setup
- CUDA and Python environment
- Ollama model setup
- REST API verification
- LangChain, ChromaDB, and FastAPI dependencies

## Week 1 Focus
Week 1 focused on platform bring-up and AI environment preparation.

Team Alpha completed laptop-based ROS2 practice, keyboard teleoperation verification, SSH and LIDAR workflow preparation, and digital twin simulation exploration. Xavier NX, JetPack flashing, real LIDAR verification, and final SSH verification are hardware-dependent tasks and remain pending until hardware is available.

## Repository Structure
```text
AI-Robotic-Proxy/
├── README.md
├── team_alpha/
│   ├── docs/
│   ├── ros2_practice/
│   ├── digital_twin/
│   └── setup_notes/
└── team_beta/
Current Team Alpha Work
ROS2 turtlesim practice
Keyboard teleoperation verification
LIDAR verification workflow preparation
SSH setup workflow preparation
Expo robot digital twin simulation
Hospital medicine delivery robot digital twin simulation
Hardware-Dependent Pending Work
Xavier NX configuration
JetPack flashing on Xavier NX
ROS2 Humble installation on target hardware
Real LIDAR connection and /scan verification
Remote SSH verification with Xavier NX
Real robot keyboard teleoperation
