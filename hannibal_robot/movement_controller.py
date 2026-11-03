#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class HannibaLMovementController(Node):

    def __init__(self):
        super().__init__('hannibal_movement_controller')

        self.cmd_vel_publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.command_subscriber = self.create_subscription(
            String,
            '/hannibal/move',
            self.handle_command,
            10
        )

        self.stop_timer = None

        self.get_logger().info(
            'Hanniba-L movement controller ready. '
            'Commands: forward, backward, left, right, stop'
        )

    def handle_command(self, msg):

        command = msg.data.strip().lower()

        if command == 'stop':
            self.stop_motion()
            return

        if command not in (
            'forward',
            'backward',
            'left',
            'right'
        ):
            self.get_logger().warn(
                'Invalid command. Use: forward, backward, left, right, stop'
            )
            return

        # Cancel any previous movement timer
        if self.stop_timer is not None:
            self.stop_timer.cancel()
            self.stop_timer = None

        twist = Twist()

        if command == 'forward':
            twist.linear.x = 0.5

        elif command == 'backward':
            twist.linear.x = -0.5

        elif command == 'left':
            twist.angular.z = 0.8

        elif command == 'right':
            twist.angular.z = -0.8

        self.cmd_vel_publisher.publish(twist)

        self.get_logger().info(
            f'Hanniba-L moving {command} for 1 second'
        )

        self.stop_timer = self.create_timer(
            1.0,
            self.stop_motion
        )

    def stop_motion(self):

        twist = Twist()

        self.cmd_vel_publisher.publish(twist)

        if self.stop_timer is not None:
            self.stop_timer.cancel()
            self.stop_timer = None

        self.get_logger().info('Hanniba-L stopped')

    def destroy_node(self):

        self.stop_motion()
        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = HannibaLMovementController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()