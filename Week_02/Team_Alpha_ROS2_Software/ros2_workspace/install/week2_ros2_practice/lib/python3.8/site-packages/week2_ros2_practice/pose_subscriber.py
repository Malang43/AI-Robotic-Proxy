import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class PoseSubscriber(Node):
    def __init__(self):
        super().__init__('week2_pose_subscriber')

        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )

    def pose_callback(self, msg):
        self.get_logger().info(
            f'Turtle Pose -> x: {msg.x:.2f}, y: {msg.y:.2f}, '
            f'theta: {msg.theta:.2f}, linear_velocity: {msg.linear_velocity:.2f}, '
            f'angular_velocity: {msg.angular_velocity:.2f}'
        )


def main(args=None):
    rclpy.init(args=args)
    node = PoseSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
