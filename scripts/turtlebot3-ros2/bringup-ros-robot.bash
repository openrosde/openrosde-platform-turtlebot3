#!/bin/bash

# This script brings up the TurtleBot3 robot on ROS 2 by SSH, as 'BRINGUP-ROS-ROBOT.bash' calls it when 'turtlebot3-ros2' is the active platform.
# It runs with every 'OPENROSDE_*' variable exported by 'scripts/load-openrosde-env.bash'.
# The robot runs ROS 2 on its own computer, set up as the TurtleBot3 manual of ROBOTIS describes, with the user 'ubuntu' and the workspace '~/turtlebot3_ws', and shares the domain 'OPENROSDE_ROS_DOMAIN_ID' of the container.
# https://emanual.robotis.com/docs/en/platform/turtlebot3/sbc_setup/
# ROS 2 has no master, so the argument that 'BRINGUP-ROS-ROBOT.bash' passes is not read.
#
# Usage: bash ./scripts/turtlebot3-ros2/bringup-ros-robot.bash [rosmaster-hostname]

################################################################################

# Stop the launches of an earlier bringup inside the robot, then start its bringup, with the motors, the LiDAR, and the robot state publisher, and its camera.
ssh -f -t -l ubuntu "${OPENROSDE_ROBOT_HOSTNAME}" 'bash -c "
for ROS_SETUP_FILE in /opt/ros/*/setup.bash; do source \${ROS_SETUP_FILE}; done;
source ~/turtlebot3_ws/install/setup.bash;
export ROS_DOMAIN_ID='"${OPENROSDE_ROS_DOMAIN_ID}"';
export TURTLEBOT3_MODEL=waffle_pi;
export LDS_MODEL=LDS-01;
pkill -INT -f \"ros2 launch\";
sleep 5;
ros2 launch turtlebot3_bringup robot.launch.py > /tmp/turtlebot3-bringup.log 2>&1 &
sleep 5;
ros2 launch turtlebot3_bringup camera.launch.py > /tmp/turtlebot3-camera.log 2>&1 &
sleep 5;
echo "Done"
"'
