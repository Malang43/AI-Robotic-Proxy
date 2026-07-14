import rclpy
from rclpy.node import Node


class SimpleNode(Node):
    def __init__(self):
        super().__init__('simple_node')
        self.counter = 0
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        self.counter += 1
        self.get_logger().info(f'Week 2 ROS2 simple node is running... Count: {self.counter}')


def main(args=None):
    rclpy.init(args=args)
    node = SimpleNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
