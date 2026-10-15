#!/bin/bash

# This script sets the shell configuration of the TurtleBot3 platform on ROS 2 inside the Docker container.
# 'docker/openrosde-base/scripts/initialize-bash-shell.bash' of the core sources it when 'turtlebot3-ros2' is the active platform.
#
# Usage: source ${OPENROSDE_CONTAINER_ROOT_DIR}/scripts/turtlebot3-ros2/initialize-bash-shell.bash

################################################################################

# Select the TurtleBot3 model name and the model of its LiDAR, which the launch files of ROBOTIS read.
# https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/#set-turtlebot3-model-name-1
export TURTLEBOT3_MODEL=waffle_pi
export LDS_MODEL=LDS-01

# Name the launch package of the platform, which both ROS name 'openrosde_turtlebot3_launch', rather than the name 'openrosde_turtlebot3-ros2_launch' that the core derives from the platform, which no ROS package may take.
OPENROSDE_LAUNCH_PACKAGE=openrosde_turtlebot3_launch
export OPENROSDE_LAUNCH_PACKAGE
