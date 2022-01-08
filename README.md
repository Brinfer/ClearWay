<p align="center">
    <img src="documents/base/logo/clearWayLong.png" alt="Logo" height="100">
<h1 align="center"><b>ClearWay</b></h1>
</p>

<p align=center>
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg"/>
    <img src="https://img.shields.io/static/v1?style=flat&message=Python&logo=python&labelColor=FFD43B&color=306998&logoColor=3776AB&label=%20"/>
    <img src="https://img.shields.io/static/v1?style=flat&message=Raspberry&logo=Raspberry Pi&labelColor=white&color=A22846&logoColor=A22846&label=%20"/>
</p>

<p align=center>
    <img src="https://172.24.0.69/i3-fise/pfe/clearway/badges/master/coverage.svg"/>
    <img src="https://172.24.0.69/i3-fise/pfe/clearway/badges/master/pipeline.svg?job=test"/>
</p>

<details>
  <summary>Table of Contents</summary>

- [1. Main Characters of the Project](#1-main-characters-of-the-project)
- [2. License](#2-license)
- [3. About the Project](#3-about-the-project)
- [4. Installation](#4-installation)
  - [4.1. 4.1 From the source](#41-41-from-the-source)
- [5. Usage](#5-usage)
  - [5.1. Dependencies](#51-dependencies)
  - [5.2. Optional Arguments](#52-optional-arguments)
- [6. Contributing](#6-contributing)

</details>

# 1. Main Characters of the Project

- [CHAUVIN Léo](https://www.linkedin.com/in/l%C3%A9o-chauvin-41b3a4178/)
- [FRISSANT Damien](https://www.linkedin.com/in/damien-frissant-a3b779178/)
- [GAUTIER Pierre-Louis](https://www.linkedin.com/in/pierre-louis-gautier/)

</details>

# 2. License

See [`LICENSE.md`](./LICENSE.md).

# 3. About the Project

ClearWay is a school project made by 3 engineer students in 2021-2022.

The main purpose of the project is to avoid incidents and crashes between cyclists and car. Because this project is a Proof Of Concept, the operating range luminosity have to be higher than 700 lux (between sunrise and cloudy day).

There are two systems for this project:

- The first one will detect bicycles thanks to a camera. An IA is embedded to identify the cyclist. If a bicycle is detected, a message is sent to the other system.

- The second device is an electric road sign. This one is located at a crossroad. He will advise motorists that a bike is approaching to the junction by flashing.

The project is intended for communities, but he will benefit to road users and cyclists in particular who will be safer when crossing the crossroads that have this system.

# 4. Installation

## 4.1. 4.1 From the source

To install _ClearWay_ from the source files, just do :

```bash
python -m build
```

Then you just have to place the __dist__ folder in the desired environment and do

```bash
pip install dist/clearway*.whl
```

or

```bash
pip install dist/clearway*.tar.gz
```

# 5. Usage

## 5.1. Dependencies

A version of __Python 3.8__ minimum is required. In the different sub-projects, a __requirements.txt__ file will list the different packages needed and their version. To install them easily use the command :

```bash
pip install -r requirements.txt
```

## 5.2. Optional Arguments

```text
usage: clearway [OPTIONS] --yolo-cfg YOLO_CFG --yolo-weights YOLO_WEIGHTS --config CONFIG

optional arguments:
  -h, --help            show this help message and exit
  --panel_gpios PANEL_GPIOS
                        tells the program which gpio to use
  --no-gpio             tells the program to not use the GPIOs, only the logs will be displayed
  --use-gpio            tells the program to use the GPIOs
  --on-raspberry        tells the program if we are using a raspberry or a computer
  --see-rtp             tells the program if we want to see a window with the real-time processing in it
  -i INPUT_PATH, --input-path INPUT_PATH
                        the path to the input video to be analyzed rather than using the video stream from the camera
  -o OUTPUT_PATH, --output-path OUTPUT_PATH
                        the path to the folder that will contain the output video with boxes around detected bicycles
  -v {WARNING,INFO,DEBUG}, --verbosity {WARNING,INFO,DEBUG}
                        indicates the level of verbosity
  -V, --version         print the ClearWay version and exit

required arguments:
  --yolo-weights YOLO_WEIGHTS
                        the path to the weights file of yolo, required if the --config argument is not provided.
                        The configuration file must then contain the path to the yolo file
  --yolo-cfg YOLO_CFG   the path to the configuration file of yolo, required if the argument --config is not provided.
                        The configuration file must then contain the path to the yolo file.
  -c CONFIG, --config CONFIG
                        the path to the config file, required if the arguments --yolo-cfg and --yolo-weights are not provided.
                        All parameters contained in the configuration file can be overloaded with optional arguments.
  --size SIZE           the size of the images converted to blob (320 or 416 recommended), required if the argument --config is not provided.
                        The configuration file must then contain the size of the image
```

# 6. Contributing

After cloning the repository, perform the following instruction :

```bash
git config core.hooksPath .githooks
```

This instruction makes sure that everyone is using the same git hook.
