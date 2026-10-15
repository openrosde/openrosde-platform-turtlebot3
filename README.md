# OpenRoSDE Platform TurtleBot3

The Robotis TurtleBot3 (Waffle Pi) platform of [OpenRoSDE](https://gitlab.com/coarobo/SDE), read "Open Robotic SDE", the open-source Software Development Environment for collaborative robotics research maintained by [Coarobo GK](https://coarobo.com/).
It is an extension that OpenRoSDE finds by name once it is cloned into `extensions/openrosde-platform-turtlebot3/` of the core.

[![Pipeline](https://gitlab.com/coarobo/openrosde/openrosde-platform-turtlebot3/badges/main/pipeline.svg)](https://gitlab.com/coarobo/openrosde/openrosde-platform-turtlebot3/-/pipelines)
[![ROS Noetic](https://img.shields.io/badge/ROS_Noetic-Framework-blue?logo=ros&logoColor=white)](http://wiki.ros.org/noetic)
[![Gazebo](https://img.shields.io/badge/Gazebo-Simulator-blue)](http://gazebosim.org/)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-green)](LICENSE)

## 📑 Content

[[_TOC_]]

## 🤖 Robot Platform

| Platform     | Robot                                                                                               | Documentation                                                            |
| ------------ | --------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `turtlebot3` | [Robotis TurtleBot3 (Waffle Pi)](https://emanual.robotis.com/docs/en/platform/turtlebot3/overview/) | [docs/robot-platforms/turtlebot3.md](docs/robot-platforms/turtlebot3.md) |

## 📁 Directory Structure

| Path                                    | Content                                                                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `env/turtlebot3.env`                    | Default setup of the platform, which `bash ./SWITCH-ROBOT-PLATFORM.bash turtlebot3` copies to `.env.custom` of the core. |
| `docker/turtlebot3-devel/Dockerfile`    | Platform image `turtlebot3-devel`, built on the image `openrosde-base` of the core.                                      |
| `docker/docker-compose-turtlebot3.yaml` | Docker Compose overlay of the platform.                                                                                  |
| `ros/turtlebot3_catkin_ws/`             | Catkin workspace with `openrosde_turtlebot3_launch` and `openrosde_turtlebot3_behaviors`.                                |
| `tmux/turtlebot3.panes`                 | Panes of the `tmux` sessions of the platform.                                                                            |
| `terminator/turtlebot3.config`          | Terminator layouts of the platform, until `tmux` replaces them.                                                          |
| `scripts/turtlebot3/`                   | Bringup of the robot over SSH and shell configuration of the container.                                                  |
| `ci/allowed-duplicate-nodes.txt`        | Nodes that two panes of one layout start on purpose, which the CI of the core reads.                                     |
| `docs/robot-platforms/turtlebot3.md`    | Documentation of the platform.                                                                                           |

The layout is the one of the core, which the [Extensions](https://gitlab.com/coarobo/SDE/-/blob/dev/docs/extensions.md) guide of OpenRoSDE describes.

## 🚀 Quick Start

1. Clone and set up the core of OpenRoSDE on the Ubuntu development machine, as its [Quick Start](https://gitlab.com/coarobo/SDE#-quick-start) describes:

    ```shell
    git clone https://gitlab.com/coarobo/SDE.git && cd SDE/
    bash ./SETUP-DEVEL-MACHINE.bash
    ```

2. Clone this platform into `extensions/` of the core:

    ```shell
    git clone https://gitlab.com/coarobo/openrosde/openrosde-platform-turtlebot3.git extensions/openrosde-platform-turtlebot3
    ```

3. Switch to the platform, which also clones the Git submodules of every extension and applies their patches:

    ```shell
    bash ./SWITCH-ROBOT-PLATFORM.bash turtlebot3
    ```

4. Pull or build the Docker images, then run the container and build the Catkin workspaces:

    ```shell
    bash ./BUILD-DOCKER-IMAGE.bash
    bash ./RUN-DOCKER-CONTAINER.bash
    openrosde-initialize-new-container
    ```

5. Exit the container (`Ctrl+d`) and open the `tmux` session of the platform:

    ```shell
    bash ./RUN-TMUX-SESSION.bash
    ```

The core needs no change to find the platform, since `bash ./SWITCH-ROBOT-PLATFORM.bash` lists every platform of the cloned extensions.
Update the platform with `git -C extensions/openrosde-platform-turtlebot3 pull`, then `bash ./scripts/update-git-submodules.bash`.

## 📖 Documentation

| Document                                                                     | Description                                                             |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| [Robot Platforms / TurtleBot3](docs/robot-platforms/turtlebot3.md)           | Robotis TurtleBot3 (Waffle Pi) configuration, simulation, and operation |
| [Basic Usage](https://gitlab.com/coarobo/SDE/-/blob/dev/docs/basic-usage.md) | Full setup guide of the core of OpenRoSDE                               |
| [Extensions](https://gitlab.com/coarobo/SDE/-/blob/dev/docs/extensions.md)   | How OpenRoSDE finds the files of a cloned extension and tests it        |

## 🧪 Continuous Integration

The CI of the core of OpenRoSDE tests this platform at the commit that `gitlab-ci/extensions.repos` of the core pins: it builds or reuses the image `registry.gitlab.com/coarobo/sde/turtlebot3-devel`, builds the Catkin workspaces in it, and checks every launch entry point of the panes.
It publishes the image as `dev` or `main` from those branches of the core, and under the tag of a release of the core, such as `v3.0.0`.

`.gitlab-ci.yml` of this repository triggers a pipeline of the core on `dev` for every change, with `OPENROSDE_CI_EXTENSION_OVERRIDE` set to this project, its branch, and its commit, so that the core tests only the setups that run this platform, at that commit, and publishes nothing.

## 🐛 Reporting Issues

Please report any issue of this platform using the GitLab issue tracker: [https://gitlab.com/coarobo/openrosde/openrosde-platform-turtlebot3/-/issues](https://gitlab.com/coarobo/openrosde/openrosde-platform-turtlebot3/-/issues).

## 📜 Third-Party Software

This repository holds no third-party code.
The image `turtlebot3-devel` and the Catkin workspace bring the third-party software below, each under its own license, as [`NOTICE`](NOTICE) records.

| Component                                                                                     | Source                                                                                                                   | License                                                                     |
| --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| TurtleBot3 packages of ROBOTIS: `turtlebot3`, `turtlebot3_msgs`, and `turtlebot3_simulations` | Debian packages `ros-noetic-turtlebot3*` of the image `turtlebot3-devel`, from https://github.com/ROBOTIS-GIT/turtlebot3 | [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) (ROBOTIS CO., LTD.) |
| ROS Noetic, Gazebo, FlexBE, and the other packages of the image `openrosde-base`              | The core of OpenRoSDE, https://gitlab.com/coarobo/SDE                                                                    | Per upstream, such as BSD, Apache-2.0, or MIT                               |

## 🕰️ History

The files of this platform come from the core of OpenRoSDE, [`coarobo/SDE`](https://gitlab.com/coarobo/SDE), at commit [`041d164`](https://gitlab.com/coarobo/SDE/-/commit/041d164201db41ac35db5efd7889e6424a84deca) of `dev`, where their earlier history lives.

## ⚖️ License

```
Copyright 2019 Coarobo GK

Licensed under the Apache License, Version 2.0.
```

See [`LICENSE`](LICENSE) for the license, and [`NOTICE`](NOTICE) for the MIT notice of the earlier code and the notices of third-party software.
