# TurtleBot3 (Waffle Pi) on ROS 2

Platform-specific documentation for the Robotis [TurtleBot3 (Waffle Pi)](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/) on ROS 2 Lyrical Luth within OpenRoSDE, beside the platform `turtlebot3` of the same robot on ROS 1 Noetic, which [turtlebot3.md](turtlebot3.md) describes.

## 🔗 External Resources

- Official manual: [https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/)
- GitHub repository: [https://github.com/ROBOTIS-GIT/turtlebot3](https://github.com/ROBOTIS-GIT/turtlebot3)
- GitHub repository of the simulation: [https://github.com/ROBOTIS-GIT/turtlebot3_simulations](https://github.com/ROBOTIS-GIT/turtlebot3_simulations)
- ROS 2 in OpenRoSDE: [https://github.com/openrosde/openrosde/blob/dev/docs/ros2.md](https://github.com/openrosde/openrosde/blob/dev/docs/ros2.md)

## ⚙️ Platform Configuration

Clone this repository into `extensions/` of the core of OpenRoSDE, then switch to the platform on ROS 2:

```shell
git clone https://github.com/openrosde/openrosde-platform-turtlebot3.git extensions/openrosde-platform-turtlebot3
bash ./SWITCH-ROBOT-PLATFORM.bash turtlebot3-ros2
```

The template `env/turtlebot3-ros2.env` sets `OPENROSDE_ROS_VERSION=2` and `OPENROSDE_ROS_DISTRO=lyrical`, so the platform runs on the base image `openrosde-base-ros2` of the core, Ubuntu 26.04 with ROS 2 Lyrical and Gazebo Jetty.
It also sets `OPENROSDE_ROS_DOMAIN_ID=30`, the domain that the TurtleBot3 manual of ROBOTIS uses, which the robot must share.

| Item | Value |
| --- | --- |
| Image | `turtlebot3-ros2-devel`, built from `docker/turtlebot3-ros2-devel/Dockerfile` on `openrosde-base-ros2` |
| Workspace | `ros2/turtlebot3_colcon_ws/`, with `openrosde_turtlebot3_launch` and the Git submodule `turtlebot3` of ROBOTIS |
| Launch package | `openrosde_turtlebot3_launch`, which `scripts/turtlebot3-ros2/initialize-bash-shell.bash` names |
| Model | `TURTLEBOT3_MODEL=waffle_pi` and `LDS_MODEL=LDS-01`, set by the same script |
| Panes | `tmux/turtlebot3-ros2.panes`, in the layouts `default-gazebo` and `default-realworld` |

## 📦 Packages

- The ROS 2 repositories release the messages of the TurtleBot3, the driver library of its motors, and its simulation for Lyrical, which the image installs: `ros-lyrical-turtlebot3-msgs`, `ros-lyrical-dynamixel-sdk`, and `ros-lyrical-turtlebot3-simulations`.
- They release no `turtlebot3` for Lyrical, so its packages, such as `turtlebot3_description`, `turtlebot3_navigation2`, `turtlebot3_bringup`, and `turtlebot3_node`, build from the Git submodule `ros2/turtlebot3_colcon_ws/src/turtlebot3`, pinned at the tag `2.3.7` (commit `fc817ce3073af1d6032397c64504134882af5e9a`).
- `patches/ros2/turtlebot3_colcon_ws/src/turtlebot3/0001-build-on-lyrical.patch` builds `turtlebot3_node` on Lyrical, with the headers `.hpp` of `message_filters`, `tf2`, and `tf2_ros`, and the QoS that a subscriber of `message_filters` now asks for.
- Cartographer is not released for Lyrical, so the mapping runs SLAM Toolbox, and `turtlebot3_cartographer` builds but cannot run.
- The world of the simulation includes the models `Ground Plane` (version 5) and `Sun` (version 3) of OpenRobotics from Gazebo Fuel, under CC0 1.0, which the image caches, checked by version and SHA-256, so that the simulation runs with no network.

## 🎮 Gazebo Simulation

Open the `tmux` session of the simulation, whose panes start these launch files, each after a key press:

```shell
bash ./RUN-TMUX-SESSION.bash #[docker-project] default-gazebo
```

| Launch File | Description |
| --- | --- |
| `turtlebot3_bringup_default_gazebo.launch.py` | The TurtleBot3 in its world of Gazebo, with the bridge of `ros_gz` and `robot_state_publisher`, and `gui:=false` for the server alone with headless rendering |
| `turtlebot3_rviz_default_gazebo.launch.xml` | RViz with the layout of the navigation, on the clock of the simulation |
| `turtlebot3_navigation_default_gazebo.launch.xml` | Nav2 with the map of the world and the parameters of the model, without the RViz of the upstream launch file |
| `turtlebot3_mapping_default.launch.xml use_sim_time:=true` | SLAM Toolbox on the clock of the simulation |

The panes of the core on ROS 2 add the rqt suite, `rosbridge` with the file service of the robot model on port `9090`, and the user example.
Nav2 waits for an initial pose before it plans, so give it with the tool `2D Pose Estimate` of RViz at the position of the robot, as the manual of ROBOTIS describes, while SLAM Toolbox maps from the start.
Drive the robot with `ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -p stamped:=true` in a shell of the container, since the TurtleBot3 reads a `geometry_msgs/msg/TwistStamped` on `/cmd_vel`.

## 🤖 Real Robot

> [!WARNING]
> The robot side of ROS 2 has not run on a real TurtleBot3 yet.
> A TurtleBot3 set up as [turtlebot3.md](turtlebot3.md) describes runs ROS Kinetic, so it needs a computer set up with ROS 2 as the manual of ROBOTIS describes before this platform can reach it.

1. Set up the computer of the robot with ROS 2 and the workspace `~/turtlebot3_ws`, with the user `ubuntu`, as the SBC setup of the manual describes: [https://emanual.robotis.com/docs/en/platform/turtlebot3/sbc_setup/](https://emanual.robotis.com/docs/en/platform/turtlebot3/sbc_setup/).
2. Set `OPENROSDE_ROS_MASTER_HOSTNAME` to the host name of the robot in `.env.custom`, so that the discovery of ROS 2 reaches it as a static peer, and keep the domain of the robot in `OPENROSDE_ROS_DOMAIN_ID`.
3. Bring up the robot, whose motors, LiDAR, robot state publisher, and camera start over SSH:

    ```shell
    bash ./BRINGUP-ROS-ROBOT.bash <robot-hostname> #[docker-project]
    ```

4. Open the `tmux` session of the real robot, with RViz and the mapping:

    ```shell
    bash ./RUN-TMUX-SESSION.bash #[docker-project] default-realworld
    ```

> [!IMPORTANT]
> The container and the robot must run the same middleware, Fast DDS by default, in the same domain, with a ROS 2 distribution whose messages match those of Lyrical.

## 🧪 Continuous Integration

- The CI of the core builds `turtlebot3-ros2-devel` on the base image of ROS 2 and tests the setup `turtlebot3-ros2`: it builds the colcon workspace, checks the robot model through `rosbridge`, and loads every launch entry point of the panes with `ros2 launch --show-args`.
- `ci/check-in-container.bash` then runs `ci/check-rosbridge.bash` for this platform alone, in the container with no network: it starts `ci/turtlebot3_rosbridge_check.launch.xml`, the TurtleBot3 in Gazebo without a window and `rosbridge`, and `ci/check-rosbridge.py` checks `/clock`, `/joint_states`, `/tf`, `/tf_static`, `/scan`, `/odom`, and `robot_description`, fetches every mesh of the description and its GLB through `/file_server/get_file`, and drives the simulated robot until `/odom` shows it moved, then stops it.
- `waffle_base.stl` of `turtlebot3_description`, the base of the Waffle, gives a GLB above `max_file_size`, which the robot model check reports, since it lies in the Git submodule, while the Waffle Pi of this platform uses `waffle_pi_base.stl`.
