<p align="center">
    <img src="documents/base/logo/clearWayLong.png" alt="Logo" height="80">
<h1 align="center"><b>ClearWay</b></h1>
</p>

- [1. Main Characters of the Project](#1-main-characters-of-the-project)
- [2. License](#2-license)
- [3. About the Project](#3-about-the-project)
- [4. Installation](#4-installation)
  - [4.1. Python](#41-python)
  - [4.2. Latex](#42-latex)

## 1. Main Characters of the Project

- [CHAUVIN Léo](https://www.linkedin.com/in/l%C3%A9o-chauvin-41b3a4178/)
- [FRISSANT Damien](https://www.linkedin.com/in/damien-frissant-a3b779178/)
- [GAUTIER Pierre-Louis](https://www.linkedin.com/in/pierre-louis-gautier/)

## 2. License

See [`LICENCE.md`](./LICENCE.md).

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

### 4.1. Python

In order to use the git hooks implementer correctly, a version of __Python 3.6__ minimum is required.

### 4.2. Latex

The drafting of documents is done in latex, some packages are necessary:

- [ae](https://www.ctan.org/pkg/ae)
-[aeguill](https://www.ctan.org/pkg/aeguill) This package manages culturally-determined typographical (and other)
          rules for a wide range of languages.
- [babel](https://www.ctan.org/pkg/babel) This package manages culturally-determined typographical (and other) rules
          or a wide range of languages.
- [enumitem](https://www.ctan.org/pkg/enumitem) This package provides user control over the layout of the three basic
          list environments: enumerate, itemize and description.
- [fancyhdr](https://www.ctan.org/pkg/fancyhdr) The package provides extensive facilities, both for constructing headers
          and footers, and for controlling their use.
- [geometry](https://www.ctan.org/pkg/geometry) The package provides an easy and flexible user interface to customize
          page layout, implementing auto-centering and auto-balancing mechanisms.
- [glossaries](https://www.ctan.org/pkg/glossaries) This package provides improvements and extra features
          to the glossaries package.
- [graphicx](https://www.ctan.org/pkg/graphicx) The package builds upon the graphics package, providing a key-value
          interface for optional arguments to the `\includegraphics` command.
- [hyperref](https://www.ctan.org/pkg/hyperref) The __hyperref__ package is used to handle cross-referencing commands in
          Latex to produce hypertext links in the document.
- [kvoption](https://www.ctan.org/pkg/kvoptions) This package offers support for package authors who want to use options
          in key-value format for their package options.
- [lastpage](https://www.ctan.org/pkg/lastpage) Reference the number of pages in your Latex document through the
          introduction of a new label.
- [lmodern](https://www.ctan.org/tex-archive/info/lmodern) Provide some symbol.
- [multirow](https://www.ctan.org/pkg/multirow) The package has a lot of flexibility, including an option for specifying
          an entry at the “natural” width of its text.
- [tabularx](https://www.ctan.org/pkg/tabularx) The package defines an environment __tabularx__, an extension of
          __tabular__ which has an additional column designator, X, which creates a paragraph-like column whose width automatically
          expands so that the declared width of the environment is filled.
- [titlesec](https://www.ctan.org/pkg/titlesec) A package providing an interface to sectioning commands for selection
          from various title styles.
- [xcolor](https://www.ctan.org/pkg/xcolor) The package starts from the basic facilities of the __color__ package,
          and provides easy driver-independent access.
