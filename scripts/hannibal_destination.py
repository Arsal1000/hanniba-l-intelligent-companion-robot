import math
import re

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from action_msgs.msg import GoalStatus
from std_msgs.msg import String
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped


# Existing bedside and kitchen coordinates have been tested.
# New coordinates are candidates and must be validated in Gazebo.
DESTINATIONS = {
    'start': (-3.0, -2.0, 0.0),
    'starting_position': (-3.0, -2.0, 0.0),
    'home': (-3.0, -2.0, 0.0),
    'bedside': (-2.5, 1.4, 0.0),
    'bed': (-2.5, 1.4, 0.0),
    'bedroom': (-2.5, 1.4, 0.0),

    'kitchen': (2.5, 2.5, 0.0),

    'living_area': (-2.5, -0.5, 0.0),
    'living_room': (-2.5, -0.5, 0.0),

    'table_side': (2.0, -0.9, -math.pi / 2.0),
    'table': (2.0, -0.9, -math.pi / 2.0),
}



def parse_destination_command(raw):
    """Normalize natural-language text into an existing destination or action."""
    text = raw.strip().lower()
    text = text.replace("hanniba-l", " ")
    text = text.replace("hannibal", " ")
    text = re.sub(r"[^a-z0-9_\s'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    if text in ("stop", "stop moving", "cancel", "cancel navigation"):
        return "cancel"

    if text in (
        "help", "list", "destinations", "show destinations",
        "what can you do"
    ):
        return "help"

    if text in (
        "go home", "return home", "go back home", "return to home",
        "return to start", "go to start",
        "return to the starting position",
        "go to the starting position",
        "return to the starting point",
        "go back to the starting position",
    ):
        return "start"

    text = re.sub(
        r"^(please\s+)?(can you\s+)?(please\s+)?", "", text
    ).strip()

    text = re.sub(
        r"^(go|move|head|navigate|travel)\s+(to\s+)?",
        "", text
    ).strip()

    text = re.sub(r"^(take me|bring me)\s+(to\s+)?", "", text).strip()
    text = re.sub(r"^(the|my)\s+", "", text).strip()

    text = text.replace("-", " ")
    text = re.sub(r"\s+", "_", text).strip("_")

    aliases = {
        "livingroom": "living_room",
        "bed_room": "bedroom",
        "bed_side": "bedside",
        "table_side": "table_side",
        "starting_position": "start",
        "starting_point": "start",
    }

    return aliases.get(text, text)


class HannibaLDestination(Node):
    def __init__(self):
        super().__init__('hannibal_destination')

        self.client = ActionClient(
            self, NavigateToPose, '/navigate_to_pose'
        )

        self.sub = self.create_subscription(
            String, '/hannibal/destination', self.handle_command, 10
        )

        self.status_pub = self.create_publisher(
            String, '/hannibal/navigation_status', 10
        )

        self.active = False
        self.goal_handle = None
        self.current_destination = None

        self.get_logger().info(
            'Ready. Destinations: start, home, starting_position, '
            'bedside, bedroom, kitchen, living_area, living_room, '
            'table_side, table. '
            'Send "cancel" to cancel an active goal.'
        )
        self.publish_status('READY')

    def publish_status(self, text):
        msg = String()
        msg.data = text
        self.status_pub.publish(msg)
        self.get_logger().info(text)

    def handle_command(self, msg):
        name = parse_destination_command(msg.data)

        if name in ("cancel", "stop"):
            self.cancel_navigation()
            return

        if name in ("help", "list", "destinations"):
            self.publish_status(
                "DESTINATIONS: start, home, bedside, bedroom, kitchen, "
                "living_area, living_room, table_side, table. "
                "Commands: go to <destination>, return home, stop, help."
            )
            return

        if name not in DESTINATIONS:
            self.publish_status(
                f'REJECTED: unknown destination "{name}". '
                'Send help to list destinations.'
            )
            return

        if self.active:
            self.publish_status(
                f'BUSY: already navigating to '
                f'{self.current_destination}; send cancel first.'
            )
            return

        if not self.client.wait_for_server(timeout_sec=2.0):
            self.publish_status(
                'ERROR: Nav2 /navigate_to_pose is unavailable.'
            )
            return

        x, y, yaw = DESTINATIONS[name]

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal.pose.pose.orientation.w = math.cos(yaw / 2.0)

        self.active = True
        self.current_destination = name
        self.goal_handle = None

        self.publish_status(
            f'REQUESTED: {name} at x={x:.2f}, y={y:.2f}'
        )

        future = self.client.send_goal_async(goal)
        future.add_done_callback(self.goal_response)

    def goal_response(self, future):
        try:
            handle = future.result()
        except Exception as exc:
            self.finish(f'ERROR: failed to submit goal: {exc}')
            return

        if not handle.accepted:
            self.finish(
                f'REJECTED_BY_NAV2: {self.current_destination}'
            )
            return

        self.goal_handle = handle
        self.publish_status(
            f'ACCEPTED: navigating to {self.current_destination}'
        )

        result_future = handle.get_result_async()
        result_future.add_done_callback(self.goal_result)

    def goal_result(self, future):
        destination = self.current_destination

        try:
            result = future.result()
            status = result.status
        except Exception as exc:
            self.finish(f'ERROR: could not read navigation result: {exc}')
            return

        if status == GoalStatus.STATUS_SUCCEEDED:
            self.finish(f'SUCCEEDED: reached {destination}')
        elif status == GoalStatus.STATUS_CANCELED:
            self.finish(f'CANCELED: navigation to {destination}')
        elif status == GoalStatus.STATUS_ABORTED:
            self.finish(
                f'FAILED: Nav2 aborted navigation to {destination}'
            )
        else:
            self.finish(
                f'FAILED: navigation to {destination}, '
                f'action status={status}'
            )

    def cancel_navigation(self):
        if not self.active or self.goal_handle is None:
            self.publish_status('NO_ACTIVE_GOAL: nothing to cancel')
            return

        self.publish_status(
            f'CANCEL_REQUESTED: {self.current_destination}'
        )
        future = self.goal_handle.cancel_goal_async()
        future.add_done_callback(self.cancel_response)

    def cancel_response(self, future):
        try:
            response = future.result()
            if not response.goals_canceling:
                self.publish_status(
                    'CANCEL_NOT_ACCEPTED: Nav2 did not accept cancellation'
                )
        except Exception as exc:
            self.publish_status(f'CANCEL_ERROR: {exc}')

    def finish(self, message):
        self.publish_status(message)
        self.active = False
        self.goal_handle = None
        self.current_destination = None


def main(args=None):
    rclpy.init(args=args)
    node = HannibaLDestination()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
