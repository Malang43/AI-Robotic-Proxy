import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class TopicSubscriber(Node):
    def __init__(self):
        super().__init__('week2_topic_subscriber')
        self.subscription = self.create_subscription(
            String,
            'week2_status',
            self.listener_callback,
            10
        )

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = TopicSubscriber()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
