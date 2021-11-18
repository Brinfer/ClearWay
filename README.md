<p align="center">
    <img src="documents/base/logo/clearWayLong.png" alt="Logo" height="100">
<h1 align="center"><b>ClearWay</b></h1>
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
  - [5.2. Options](#52-options)
    - [5.2.1. Optimized](#521-optimized)
    - [5.2.2. `--no-gpio`](#522---no-gpio)
- [6. Contributing](#6-contributing)

</details>

# 1. Main Characters of the Project

- [CHAUVIN Léo](https://www.linkedin.com/in/l%C3%A9o-chauvin-41b3a4178/)
- [FRISSANT Damien](https://www.linkedin.com/in/damien-frissant-a3b779178/)
- [GAUTIER Pierre-Louis](https://www.linkedin.com/in/pierre-louis-gautier/)

</details>

# 2. License

See [`LICENCE.md`](./LICENCE.md).

# 3. About the Project

ClearWay is a school project made by 3 engineer students in 2021-2022.

The main purpose of the project is to avoid incidents and crashes between cyclists and motorists. Because this project is a Proof Of Concept, the operating range luminosity have to be higher than 700 lux (between sunrise and cloudy day).

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

## 5.2. Options

### 5.2.1. Optimized

Remove assert statements and any code conditional on the value of `__debug__`. The consequence of this is that the logs are displayed only in the log file.

```bash
python -O clearway
```

### 5.2.2. `--no-gpio`

Tells the program that it does not want to use the GPIOs, only the logs will be displayed.

```bash
clearway --no-gio
```

# 6. Contributing

After cloning the repository, perform the following instruction :

```bash
git config core.hooksPath .githooks
```

This instruction makes sure that everyone is using the same git hook.
