#!/bin/bash

# This script checks that a client reaches the TurtleBot3 on ROS 2 through 'rosbridge' alone, with its robot model, as part of the CI of OpenRoSDE.
# It starts 'ci/turtlebot3_rosbridge_check.launch.xml': the TurtleBot3 in Gazebo without a window, with the server alone and headless rendering, and 'rosbridge' on port 9090 with the file service, as 'openrosde_launch:rosbridge_server_default.launch.xml' starts them.
# The WebSocket client 'ci/check-rosbridge.py' then connects to port 9090 and checks '/clock', '/joint_states', '/tf', '/tf_static', '/scan', and the transient local topic 'robot_description', fetches every mesh of the description and its GLB through '/file_server/get_file', and drives the simulated robot with a 'geometry_msgs/msg/TwistStamped' on '/cmd_vel' until '/odom' moves, then stops it.
# It starts nothing in a container with a network interface other than the loopback that is up, so that only the simulated robot can move, as in the container of the CI, which is disconnected from every network before any check runs.
# 'gitlab-ci/check-no-motion.bash' of the core allows its launch file, since 'ci/allowed-simulation-launches.txt' names it.
#
# Usage: bash ./ci/check-rosbridge.bash [timeout]
#
# [timeout]: Seconds that the simulation and the topics may take to come up.
#            Default value is '240'.

################################################################################

# Resolve the folder of the checks, and name the log of the launch file and the timeout.
OPENROSDE_TURTLEBOT3_CI_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENROSDE_TURTLEBOT3_LAUNCH_LOG_FILE="$(mktemp /tmp/openrosde-turtlebot3-rosbridge-XXXXXX.log)"
OPENROSDE_TURTLEBOT3_CHECK_TIMEOUT="$1"
if [ -z "${OPENROSDE_TURTLEBOT3_CHECK_TIMEOUT}" ]; then
  OPENROSDE_TURTLEBOT3_CHECK_TIMEOUT=240
fi

# Refuse to start any node while a network interface other than the loopback is up, whose flags carry 'IFF_UP' (0x1).
# An entry of '/sys/class/net/' without flags, such as 'bonding_masters', is no interface.
for OPENROSDE_TURTLEBOT3_NETWORK_INTERFACE_DIR in /sys/class/net/*; do
  OPENROSDE_TURTLEBOT3_NETWORK_INTERFACE="$(basename "${OPENROSDE_TURTLEBOT3_NETWORK_INTERFACE_DIR}")"
  if [ "${OPENROSDE_TURTLEBOT3_NETWORK_INTERFACE}" = "lo" ] || [ ! -f "${OPENROSDE_TURTLEBOT3_NETWORK_INTERFACE_DIR}/flags" ]; then
    continue
  fi
  if (( $(cat "${OPENROSDE_TURTLEBOT3_NETWORK_INTERFACE_DIR}/flags") & 0x1 )); then
    echo "Error: The network interface '${OPENROSDE_TURTLEBOT3_NETWORK_INTERFACE}' is up, so this check starts no node: run it in a container without network, as the CI does."
    exit 1
  fi
done

################################################################################

# Keep the discovery of ROS 2 on the loopback, in a domain of its own, apart from the nodes that an earlier check of the job left, and select the TurtleBot3 model as the shell of the platform does.
export ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST
export ROS_DOMAIN_ID=77
unset ROS_STATIC_PEERS
source "${OPENROSDE_TURTLEBOT3_CI_DIR}/../scripts/turtlebot3-ros2/initialize-bash-shell.bash"

# Stop every node of the launch file, Gazebo included, by stopping its process group, then print the end of its log when the check failed.
function openrosde-turtlebot3-stop-launch () {
  local OPENROSDE_TURTLEBOT3_CHECK_EXIT_CODE=$?
  local OPENROSDE_TURTLEBOT3_WAITED_SECONDS
  if [ -n "${OPENROSDE_TURTLEBOT3_LAUNCH_PID}" ]; then
    kill -INT -- "-${OPENROSDE_TURTLEBOT3_LAUNCH_PID}" > /dev/null 2>&1
    for OPENROSDE_TURTLEBOT3_WAITED_SECONDS in $(seq 1 30); do
      kill -0 -- "-${OPENROSDE_TURTLEBOT3_LAUNCH_PID}" > /dev/null 2>&1 || break
      sleep 1
    done
    kill -KILL -- "-${OPENROSDE_TURTLEBOT3_LAUNCH_PID}" > /dev/null 2>&1
  fi
  if [ "${OPENROSDE_TURTLEBOT3_CHECK_EXIT_CODE}" -ne 0 ]; then
    echo "End of the log of 'ci/turtlebot3_rosbridge_check.launch.xml':"
    tail -n 80 "${OPENROSDE_TURTLEBOT3_LAUNCH_LOG_FILE}"
  fi
  rm -f "${OPENROSDE_TURTLEBOT3_LAUNCH_LOG_FILE}"
  exit "${OPENROSDE_TURTLEBOT3_CHECK_EXIT_CODE}"
}
trap openrosde-turtlebot3-stop-launch EXIT

################################################################################

# Wait until no earlier check of the job listens on port 9090 any more, such as the 'rosbridge' of 'gitlab-ci/check-robot-model.bash' of the core, so that the client reaches the 'rosbridge' of this check.
for OPENROSDE_TURTLEBOT3_WAITED_SECONDS in $(seq 1 30); do
  (echo > /dev/tcp/127.0.0.1/9090) > /dev/null 2>&1 || break
  sleep 1
done
if (echo > /dev/tcp/127.0.0.1/9090) > /dev/null 2>&1; then
  echo "Error: Port 9090 is still taken after 30 seconds, so this check cannot start a 'rosbridge' of its own."
  exit 1
fi

# Start the simulation and 'rosbridge' in a process group of their own, then run the client against 'rosbridge'.
echo "Starting the TurtleBot3 on ROS 2 in Gazebo and 'rosbridge', with no network..."
setsid ros2 launch "${OPENROSDE_TURTLEBOT3_CI_DIR}/turtlebot3_rosbridge_check.launch.xml" < /dev/null > "${OPENROSDE_TURTLEBOT3_LAUNCH_LOG_FILE}" 2>&1 &
OPENROSDE_TURTLEBOT3_LAUNCH_PID=$!
timeout "$((OPENROSDE_TURTLEBOT3_CHECK_TIMEOUT + 120))" python3 "${OPENROSDE_TURTLEBOT3_CI_DIR}/check-rosbridge.py" --timeout "${OPENROSDE_TURTLEBOT3_CHECK_TIMEOUT}"
