#!/usr/bin/env python3

import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class JDStatePublisher(Node):

    def __init__(self):
        super().__init__('jd_state_publisher')

        self.publisher = self.create_publisher(
            String,
            '/hannibal/state',
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_state
        )

        # Initial JD state
        self.mode = 'idle'
        self.location = 'home'
        self.battery = 100.0
        self.is_docked = False
        self.emergency = False

    def publish_state(self):

        state = {
            'robot': 'JD',
            'mode': self.mode,
            'location': self.location,
            'battery': self.battery,
            'is_docked': self.is_docked,
            'emergency': self.emergency
        }

        msg = String()
        msg.data = json.dumps(state)

        self.publisher.publish(msg)

        self.get_logger().info(
            f'JD state: {msg.data}'
        )


def main(args=None):
    rclpy.init(args=args)

    node = JDStatePublisher()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()