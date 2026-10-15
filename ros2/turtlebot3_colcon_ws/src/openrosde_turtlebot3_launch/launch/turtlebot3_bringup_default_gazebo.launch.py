#!/usr/bin/env python3

# https://github.com/ROBOTIS-GIT/turtlebot3_simulations
# Upstream default: $(find-pkg-share turtlebot3_gazebo)/launch/turtlebot3_world.launch.py
# OpenRoSDE adds the argument 'gui', so that a check of the CI runs the server of Gazebo alone, with headless rendering, and maximizes the window of Gazebo otherwise.

import os

from ament_index_python.packages import get_package_prefix
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable
from launch.actions import DeclareLaunchArgument
from launch.actions import ExecuteProcess
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.conditions import UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Find the launch files, the world, and the models of the TurtleBot3 in Gazebo, and the launch file of Gazebo of 'ros_gz_sim'.
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    gz_sim_launch_file = os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    world = os.path.join(turtlebot3_gazebo_dir, 'worlds', 'turtlebot3_world.world')
    gui = LaunchConfiguration('gui')

    return LaunchDescription([
        # Configure the Gazebo window and the initial position of the TurtleBot3 robot.
        DeclareLaunchArgument('gui', default_value='true', description='Open the window of Gazebo, or else run its server alone with headless rendering'),
        DeclareLaunchArgument('x_pose', default_value='-2.0', description='Initial position of the robot along x'),
        DeclareLaunchArgument('y_pose', default_value='-0.5', description='Initial position of the robot along y'),

        # Let Gazebo find the models of the TurtleBot3.
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', os.path.join(turtlebot3_gazebo_dir, 'models')),

        # Start the server of Gazebo with the world of the TurtleBot3, with headless rendering when no window opens, then its window.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch_file),
            launch_arguments={'gz_args': ['-r -s -v2 ', world], 'on_exit_shutdown': 'true'}.items(),
            condition=IfCondition(gui)),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch_file),
            launch_arguments={'gz_args': ['-r -s -v2 --headless-rendering ', world], 'on_exit_shutdown': 'true'}.items(),
            condition=UnlessCondition(gui)),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch_file),
            launch_arguments={'gz_args': '-g -v2 ', 'on_exit_shutdown': 'true'}.items(),
            condition=IfCondition(gui)),

        # Spawn the TurtleBot3 robot with the bridge of its topics, and publish its description with 'robot_state_publisher'.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(turtlebot3_gazebo_dir, 'launch', 'spawn_turtlebot3.launch.py')),
            launch_arguments={'x_pose': LaunchConfiguration('x_pose'), 'y_pose': LaunchConfiguration('y_pose')}.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(turtlebot3_gazebo_dir, 'launch', 'robot_state_publisher.launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items()),

        # Maximize the Gazebo window after it opens.
        ExecuteProcess(
            cmd=[os.path.join(get_package_prefix('openrosde_launch'), 'lib', 'openrosde_launch', 'maximize-app-window.bash'), 'Gazebo'],
            condition=IfCondition(gui)),
    ])
