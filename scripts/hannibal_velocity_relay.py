import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class HannibaLVelocityRelay(Node):
    def __init__(self):
        super().__init__('hannibal_velocity_relay')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.sub = self.create_subscription(
            Twist, '/cmd_vel_nav', self.forward, 10)
        self.get_logger().info(
            'Forwarding Nav2 /cmd_vel_nav to Gazebo /cmd_vel')

    def forward(self, msg):
        self.pub.publish(msg)

rclpy.init()
node = HannibaLVelocityRelay()
try:
    rclpy.spin(node)
finally:
    node.destroy_node()
    rclpy.shutdown()
