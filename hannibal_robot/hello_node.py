import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class HelloNode(Node):

    def __init__(self):
        super().__init__('hello_node')

        self.publisher = self.create_publisher(
            String,
            'hannibal/status',
            10
        )

        self.timer = self.create_timer(1.0, self.publish_status)

    def publish_status(self):
        msg = String()
        msg.data = 'Hanniba-L ROS 2 is alive!'

        self.publisher.publish(msg)

        self.get_logger().info(f'Published: {msg.data}')


def main(args=None):
    rclpy.init(args=args)

    node = HelloNode()
    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()