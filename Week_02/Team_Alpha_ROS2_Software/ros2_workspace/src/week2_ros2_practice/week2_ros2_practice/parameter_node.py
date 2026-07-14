import rclpy
from rclpy.node import Node


class ParameterNode(Node):
    def __init__(self):
        super().__init__('week2_parameter_node')

        self.declare_parameter('robot_name', 'robotic_proxy')
        self.declare_parameter('robot_speed', 0.5)

        self.timer = self.create_timer(2.0, self.timer_callback)

    def timer_callback(self):
        robot_name = self.get_parameter('robot_name').value
        robot_speed = self.get_parameter('robot_speed').value

        self.get_logger().info(
            f'Robot Name: {robot_name}, Robot Speed: {robot_speed}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = ParameterNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
