import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TopicPublisher(Node):
    def __init__(self):
        super().__init__('week2_topic_publisher')
        self.publisher_ = self.create_publisher(String, 'week2_status', 10)
        self.counter = 0
        self.timer = self.create_timer(1.0, self.publish_message)

    def publish_message(self):
        msg = String()
        msg.data = f'Team Alpha Week 2 ROS2 topic message: {self.counter}'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.counter += 1


def main(args=None):
    rclpy.init(args=args)
    node = TopicPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
