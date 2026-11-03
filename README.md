# HANNIBA-L — Healthcare Companion Robot Simulation

HANNIBA-L is a healthcare companion robot project focused on developing a simulated mobile robot that can move through a virtual home environment.

The project combines ROS 2, Gazebo simulation, robot movement control, sensor data, mapping, and navigation-related components. The long-term goal is to develop a companion robot that can interact with people and support personalized assistance.

## Project Goals

- Simulate a mobile robot operating in a virtual home.
- Implement ROS 2 communication and robot state reporting.
- Control robot movement through ROS 2 commands.
- Integrate simulated sensors and odometry.
- Generate a map of the environment using SLAM.
- Develop and evaluate navigation components for movement between predefined destinations.

## Technology Stack

- Ubuntu 24.04
- ROS 2 Jazzy
- Gazebo Harmonic
- Python
- RViz
- SLAM Toolbox
- Navigation2 (Nav2)

## Current Features

- ROS 2 nodes for status reporting and robot state.
- A movement controller that accepts basic movement commands.
- A simulated robot model and virtual home environment.
- Sensor and odometry integration.
- A saved occupancy-grid map.
- SLAM and Nav2 configuration files.
- Navigation-related launch files and a predefined-destination command interface.

Navigation and launch behavior may depend on the local simulation setup and configuration. Not every component should be considered production-ready.

## Repository Structure

- `hannibal_robot/` — Core ROS 2 Python nodes.
- `scripts/` — Destination-command handling and velocity relay scripts.
- `models/` — Simulated robot model.
- `worlds/` — Virtual home environment.
- `launch/` — Simulation and navigation launch files.
- `config/` — SLAM and Nav2 configuration.
- `maps/` — Saved map and metadata.
- `test/` — Package test files.

## Environment

The project was developed in a WSL2 Ubuntu environment using ROS 2 Jazzy and Gazebo Harmonic. Launch files and paths may need adjustment for other installations.

## Project Status

This repository showcases the simulation and robotics software developed so far. Higher-level personalization, memory, and reasoning components are not included in this public version.

## Author

Arsal Amin

## License

No license is currently granted for reuse or redistribution. All rights are reserved by the copyright holder unless permission is granted separately.
