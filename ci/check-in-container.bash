#!/bin/bash

# This script runs the checks of the TurtleBot3 platforms inside the container of a setup, as part of the CI of OpenRoSDE.
# 'gitlab-ci/run-extension-checks.bash' of the core runs it once the workspaces of the setup are built and sourced, in the container that 'gitlab-ci/test-catkin-workspaces.bash' disconnected from every network.
#
# Usage: bash ./ci/check-in-container.bash <robot-setup>
#
# <robot-setup>: The setup that the CI tests, which activates this repository, such as 'turtlebot3' or 'turtlebot3-ros2'.

################################################################################

# Resolve the folder of the checks.
OPENROSDE_TURTLEBOT3_CI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check the TurtleBot3 on ROS 2 over 'rosbridge' in a setup of that platform only, since the setup of the TurtleBot3 on ROS 1 activates this repository too.
if [ "${OPENROSDE_ROBOT_PLATFORM}" != "turtlebot3-ros2" ]; then
  echo "Skipping the check of the TurtleBot3 on ROS 2 over 'rosbridge', since the setup '$1' runs the platform '${OPENROSDE_ROBOT_PLATFORM}'."
  exit 0
fi
bash "${OPENROSDE_TURTLEBOT3_CI_DIR}/check-rosbridge.bash"
