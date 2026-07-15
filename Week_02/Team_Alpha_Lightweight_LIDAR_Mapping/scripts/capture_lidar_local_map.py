import os
import csv
import math
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class LidarLocalMap(Node):
    def __init__(self):
        super().__init__("lidar_local_map_capture")

        self.output_dir = os.path.expanduser(
            "~/AI-Robotic-Proxy/Week_02/Team_Alpha_Lightweight_LIDAR_Mapping/output"
        )
        os.makedirs(self.output_dir, exist_ok=True)

        self.scan_messages = []
        self.required_scans = 10

        self.subscription = self.create_subscription(
            LaserScan,
            "/scan",
            self.scan_callback,
            10
        )

        self.get_logger().info("Waiting for real /scan data from RPLIDAR...")

    def scan_callback(self, msg):
        self.scan_messages.append(msg)
        self.get_logger().info(f"Captured scan {len(self.scan_messages)}/{self.required_scans}")

        if len(self.scan_messages) >= self.required_scans:
            self.process_scans()
            rclpy.shutdown()

    def process_scans(self):
        msg = self.scan_messages[-1]

        ranges = np.array(msg.ranges, dtype=float)
        angles = msg.angle_min + np.arange(len(ranges)) * msg.angle_increment

        valid = np.isfinite(ranges)
        valid = valid & (ranges >= msg.range_min)
        valid = valid & (ranges <= msg.range_max)

        ranges_valid = ranges[valid]
        angles_valid = angles[valid]

        x = ranges_valid * np.cos(angles_valid)
        y = ranges_valid * np.sin(angles_valid)

        # Save CSV data
        csv_file = os.path.join(self.output_dir, "rplidar_scan_points.csv")
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["angle_degree", "range_meter", "x_meter", "y_meter"])
            for a, r, px, py in zip(angles_valid, ranges_valid, x, y):
                writer.writerow([math.degrees(a), r, px, py])

        # Front object distance: -10 degree to +10 degree
        front_mask = (angles_valid >= math.radians(-10)) & (angles_valid <= math.radians(10))
        front_ranges = ranges_valid[front_mask]

        distance_file = os.path.join(self.output_dir, "front_object_distance.txt")
        with open(distance_file, "w") as f:
            if len(front_ranges) > 0:
                min_front = np.min(front_ranges)
                mean_front = np.mean(front_ranges)
                f.write("Front sector angle: -10 degree to +10 degree\n")
                f.write(f"Minimum front distance: {min_front:.3f} meter\n")
                f.write(f"Average front distance: {mean_front:.3f} meter\n")
            else:
                f.write("No valid object detected in front sector.\n")

        # Raw scan plot
        plt.figure(figsize=(7, 7))
        plt.scatter(x, y, s=2)
        plt.scatter([0], [0], marker="x", s=100)
        plt.title("Real RPLIDAR /scan Points")
        plt.xlabel("X distance (meter)")
        plt.ylabel("Y distance (meter)")
        plt.grid(True)
        plt.axis("equal")
        plt.xlim(-5, 5)
        plt.ylim(-5, 5)
        raw_plot_file = os.path.join(self.output_dir, "real_lidar_scan_points.png")
        plt.savefig(raw_plot_file, dpi=200, bbox_inches="tight")
        plt.close()

        # Local map-like image
        plt.figure(figsize=(7, 7))
        plt.scatter(x, y, s=3)
        plt.scatter([0], [0], marker="x", s=120)
        plt.title("Lightweight Local Scan Map from Real RPLIDAR Data")
        plt.xlabel("X distance (meter)")
        plt.ylabel("Y distance (meter)")
        plt.grid(True)
        plt.axis("equal")
        plt.xlim(-5, 5)
        plt.ylim(-5, 5)

        # Draw front direction arrow
        plt.arrow(0, 0, 1.0, 0, head_width=0.15, length_includes_head=True)
        plt.text(1.1, 0, "Front")

        map_file = os.path.join(self.output_dir, "lightweight_local_scan_map.png")
        plt.savefig(map_file, dpi=200, bbox_inches="tight")
        plt.close()

        self.get_logger().info("Saved files:")
        self.get_logger().info(csv_file)
        self.get_logger().info(distance_file)
        self.get_logger().info(raw_plot_file)
        self.get_logger().info(map_file)


def main(args=None):
    rclpy.init(args=args)
    node = LidarLocalMap()
    rclpy.spin(node)


if __name__ == "__main__":
    main()
