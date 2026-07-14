import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/farhat/AI-Robotic-Proxy/Week_02/Team_Alpha_ROS2_Software/ros2_workspace/install/week2_ros2_practice'
