# General guidelines and recommendations for writing 'Dockerfile':
# https://docs.docker.com/engine/userguide/eng-image/dockerfile_best-practices/

################################################################################

# Inherit from the OpenRoSDE base image of ROS 2 which provides all common tools.
ARG OPENROSDE_BASE_IMAGE=registry.gitlab.com/coarobo/sde/openrosde-base-ros2:main
FROM ${OPENROSDE_BASE_IMAGE}

################################################################################

# Install the TurtleBot3 robot ROS 2 dependencies.
# https://emanual.robotis.com/docs/en/platform/turtlebot3/quick-start/#pc-setup

# Gather the TurtleBot3 robot dependencies from the ROS 2 repositories: navigation, mapping with SLAM Toolbox, since Cartographer is not released for Lyrical, teleoperation, and the compressed images of the camera.
RUN apt-get update && apt-get install -y --no-install-recommends \
  ros-lyrical-compressed-image-transport \
  ros-lyrical-joy \
  ros-lyrical-nav2-bringup \
  ros-lyrical-navigation2 \
  ros-lyrical-slam-toolbox \
  ros-lyrical-teleop-twist-joy \
  ros-lyrical-teleop-twist-keyboard \
  ros-lyrical-tf-transformations \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Gather the TurtleBot3 robot packages that the ROS 2 repositories release for Lyrical: its messages, the driver library of its motors, and its simulation in Gazebo through 'ros_gz'.
# The packages of 'turtlebot3' itself, such as 'turtlebot3_description', 'turtlebot3_navigation2', and 'turtlebot3_bringup', are not released for Lyrical, so the colcon workspace of the platform builds them from the Git submodule 'ros2/turtlebot3_colcon_ws/src/turtlebot3', pinned by commit.
RUN apt-get update && apt-get install -y --no-install-recommends \
  ros-lyrical-dynamixel-sdk \
  ros-lyrical-turtlebot3-msgs \
  ros-lyrical-turtlebot3-simulations \
  && apt-get clean && rm -rf /var/lib/apt/lists/*

# Cache the models of Gazebo Fuel that the world of the TurtleBot3 includes, 'Ground Plane' and 'Sun' of OpenRobotics, so that the simulation runs with no network, as in the CI.
# https://app.gazebosim.org/OpenRobotics/fuel/models/Ground%20Plane
# https://app.gazebosim.org/OpenRobotics/fuel/models/Sun
# Fuel serves the latest version of a model only, so the build checks the version and the SHA-256 of 'model.sdf' that it served on 2026-10-15, and fails on any other, which then needs a review.
ARG OPENROSDE_FUEL_MODELS_DIR=/root/.gz/fuel/fuel.gazebosim.org/openrobotics/models
RUN . /opt/ros/lyrical/setup.sh \
  && gz fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/Ground Plane" \
  && gz fuel download -u "https://fuel.gazebosim.org/1.0/OpenRobotics/models/Sun" \
  && echo "73be59778d84e631dd0996a0adc461af5e4c8717b93da7ee9151b9ae43e3ca25  ${OPENROSDE_FUEL_MODELS_DIR}/ground plane/5/model.sdf" | sha256sum --check \
  && echo "b10a6631cfac7340ad09c2fdfeb6d950afd3ec4daf1e7d0262c14adcf612d15a  ${OPENROSDE_FUEL_MODELS_DIR}/sun/3/model.sdf" | sha256sum --check

################################################################################

# Set the platform identifier as an environment variable.
ARG OPENROSDE_ROBOT_PLATFORM=turtlebot3-ros2
ENV OPENROSDE_ROBOT_PLATFORM=${OPENROSDE_ROBOT_PLATFORM}

# Pass variables for version traceability.
ARG OPENROSDE_DOCKERFILE_COMMIT_SHORT_SHA
ENV OPENROSDE_DOCKER_IMAGE_VERSION=${OPENROSDE_DOCKERFILE_COMMIT_SHORT_SHA}
