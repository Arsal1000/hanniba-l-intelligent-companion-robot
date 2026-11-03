
from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'hannibal_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        (
            'share/ament_index/resource_index/packages',
            ['resource/' + package_name],
        ),
        (
            'share/' + package_name,
            ['package.xml'],
        ),
        (
            os.path.join('share', package_name, 'config'),
            glob('config/*.yaml'),
        ),
        (
            os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py') + glob('launch/nav2/*.launch.py'),
        ),
        (
            os.path.join('share', package_name, 'maps'),
            glob('maps/*.yaml') + glob('maps/*.pgm'),
        ),
        (
            os.path.join('share', package_name, 'worlds'),
            glob('worlds/*'),
        ),
        (
            os.path.join('share', package_name, 'models', 'jd_robot'),
            glob('models/jd_robot/*'),
        ),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='arsal',
    maintainer_email='arsal@todo.todo',
    description='Hanniba-L healthcare companion robot',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'hello_node = hannibal_robot.hello_node:main',
            'status_listener = hannibal_robot.status_listener:main',
            'jd_state_publisher = hannibal_robot.robot_state:main',
            'hannibal_movement_controller = hannibal_robot.movement_controller:main',
        ],
    },
)
