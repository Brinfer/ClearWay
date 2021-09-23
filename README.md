<p align="center">
  <a href="https://github.com/othneildrew/Best-README-Template">
    <img src="images/LogoShort.png" alt="Logo" width="80" height="80">
  </a>
<h1 align="center"><b>README for ClearWay</b></h1>

- [1. Main Characters of the Project](#1-main-characters-of-the-project)
- [2. License](#2-license)
- [3. About the Project](#3-about-the-project)
- [4. Installation](#4-installation)

## 1. Main Characters of the Project

* [CHAUVIN Léo](https://www.linkedin.com/in/l%C3%A9o-chauvin-41b3a4178/)
* [FRISSANT Damien](https://www.linkedin.com/in/damien-frissant-a3b779178/)
* [GAUTIER Pierre-Louis](https://www.linkedin.com/in/pierre-louis-gautier/)

## 2. License

Voir [`LICENCE.md`](./LICENCE.md).

## 3. About the Project

ClearWay is a school project made by 3 engineer students in 2021-2022.

The main purpose of the project is to avoid incidents and crashes between cyclists and motorists. Because this project is a Proof Of Concept, the operating range luminosity have to be higher than 700 lux (between sunrise and cloudy day).


There are two systems for this project:
- The first one will detect bicycles thanks to a camera. An IA is embedded to identify the cyclist. If a bicycle is detected, a message is sent to the other system.

- The second device is an electric road sign. This one is located at a crossroad. He will advise motorists that a bike is approaching to the junction by flashing.

The project is intended for communities, but he will benefit to road users and cyclists in particular who will be safer when crossing the crossroads that have this system.

## 4. Installation

After cloning the repository, perform the following instruction :
```bash
git config core.hooksPath .githooks
```
This instruction makes sure that everyone is using the same git hook.
