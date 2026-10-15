# openrosde_turtlebot3_launch

The `openrosde_turtlebot3_launch` package provides launch files for the Robotis TurtleBot3 platform on ROS 2, `turtlebot3-ros2`, beside the package of the same name in `ros/turtlebot3_catkin_ws/` for the platform on ROS 1.

- Maintainer: Lotfi El Hafi ([lotfi@coarobo.com](mailto:lotfi@coarobo.com)).
- Author: Lotfi El Hafi ([lotfi@coarobo.com](mailto:lotfi@coarobo.com)).

## Gazebo Simulation

Recommended startup order:

```shell
ros2 launch openrosde_turtlebot3_launch turtlebot3_bringup_default_gazebo.launch.py
ros2 launch openrosde_turtlebot3_launch turtlebot3_rviz_default_gazebo.launch.xml
ros2 launch openrosde_turtlebot3_launch turtlebot3_navigation_default_gazebo.launch.xml
```

To start the same Gazebo stack in the `tmux` session of the platform:

```shell
bash ./RUN-TMUX-SESSION.bash #[docker-project] default-gazebo
```

## Real Robot

Bring up the Robotis TurtleBot3 robot from the Ubuntu development machine, once its computer runs ROS 2:

```shell
bash ./BRINGUP-ROS-ROBOT.bash <robot-hostname> #[docker-project]
```

Then launch RViz and the mapping stack:

```shell
ros2 launch openrosde_turtlebot3_launch turtlebot3_rviz_default_realworld.launch.xml
ros2 launch openrosde_turtlebot3_launch turtlebot3_mapping_default.launch.xml
```

## Launch Files

| Launch File | Description |
| --- | --- |
| `turtlebot3_bringup_default_gazebo.launch.py` | Robotis TurtleBot3 Gazebo simulation, with `gui:=false` for the server alone with headless rendering |
| `turtlebot3_navigation_default_gazebo.launch.xml` | Navigation stack, Nav2 (Gazebo) |
| `turtlebot3_mapping_default.launch.xml` | SLAM mapping, SLAM Toolbox, with `use_sim_time:=true` in Gazebo |
| `turtlebot3_rviz_default_gazebo.launch.xml` | RViz visualization (Gazebo) |
| `turtlebot3_rviz_default_realworld.launch.xml` | RViz visualization (real robot) |

The package installs the maps of the package of ROS 1, `config/maps/`, so one copy serves both ROS.
