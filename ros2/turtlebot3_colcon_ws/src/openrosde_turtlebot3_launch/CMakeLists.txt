cmake_minimum_required(VERSION 3.10)
project(openrosde_turtlebot3_launch)

find_package(ament_cmake REQUIRED)

# Install the launch files.
install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# Install the maps of the 'openrosde_turtlebot3_launch' package of ROS 1, so that one copy serves both ROS.
install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../../../../ros/turtlebot3_catkin_ws/src/openrosde_turtlebot3_launch/config/maps
  DESTINATION share/${PROJECT_NAME}/config
)

ament_package()
