import os

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, ExecuteProcess
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

PKG = os.path.expanduser('~/hannibal_ws/src/hannibal_robot')
WORLD = os.path.join(PKG, 'worlds', 'jd_world.sdf')
MODEL_DIR = os.path.join(PKG, 'models')
MAP = os.path.join(PKG, 'maps', 'hannibal_home_mvp.yaml')
PARAMS = os.path.join(PKG, 'config', 'nav2_params.yaml')

def generate_launch_description():
    gz_share = get_package_share_directory('ros_gz_sim')
    nav_share = get_package_share_directory('nav2_bringup')

    resource_path = MODEL_DIR + os.pathsep + os.environ.get(
        'GZ_SIM_RESOURCE_PATH', ''
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(gz_share, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {WORLD}'}.items(),
    )

    lidar_static_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='hannibal_lidar_static_tf',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0.48',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'base_link',
            '--child-frame-id', 'JD/head/lidar',
        ],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='hannibal_gazebo_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav_share, 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'map': MAP,
            'use_sim_time': 'True',
            'params_file': PARAMS,
            'autostart': 'True',
        }.items(),
    )


    velocity_relay = ExecuteProcess(
        cmd=['python3', os.path.join(PKG, 'scripts', 'hannibal_velocity_relay.py')],
        output='screen',
    )

    destination_node = ExecuteProcess(
        cmd=['python3', os.path.join(PKG, 'scripts', 'hannibal_destination.py')],
        output='screen',
    )

    lifecycle_activation = ExecuteProcess(
        cmd=['bash', '-lc',
             'sleep 15; '
             'for n in /controller_server /planner_server /bt_navigator; do '
             'state=$(ros2 lifecycle get $n 2>/dev/null | awk \'{print $1}\'); '
             'if [ "$state" = unconfigured ]; then '
             'ros2 lifecycle set $n configure; state=inactive; fi; '
             'if [ "$state" = inactive ]; then ros2 lifecycle set $n activate; fi; '
             'done'],
        output='screen',
    )

    return LaunchDescription([
        velocity_relay,
        destination_node,
        lifecycle_activation,

        SetEnvironmentVariable(
            name='GZ_SIM_RESOURCE_PATH',
            value=resource_path,
        ),
        lidar_static_tf,
        gazebo,
        bridge,
        navigation,
    ])
