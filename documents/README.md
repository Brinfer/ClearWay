<details>
  <summary>Table of Contents</summary>

- [1. Research folder](#1-research-folder)
- [2. Explo folder](#2-explo-folder)
- [3. Dependencies](#3-dependencies)
  - [3.1. LaTex](#31-latex)
  - [3.2. Python](#32-python)

</details>

# 1. Research folder

A document written in [_LaTeX_](#31-latex) gathering our research on the different technologies that can be implemented in this project:

- The Communication Protocols,
- An analysis for the camera,
- The use of centralized or decentralized servers,
- A comparison of AI libraries that can be used.

# 2. Explo folder

A set of code to evaluate several artificial intelligence libraries for detecting cyclists from video:

- [ImageIA](http://www.imageai.org/),
- [OpenCV](https://opencv.org/).

The results of the evaluation are compiled in the [research folder](#1-research-folder).

# 3. Dependencies

## 3.1. LaTex

The drafting of documents is done in [_LaTeX_](https://www.latex-project.org/), some packages are necessary.

In order to use cross-references, use BibTeX for your bibliography or if you want to have a glossary, the program [latexmk](https://mg.readthedocs.io/latexmk.html) is used.
Below the list of _Latex_ packages used in the documents :

- [ae](https://www.ctan.org/pkg/ae)  A set of virtual fonts which emulates T1 coded fonts using the standard CM fonts.
- [aeguill](https://www.ctan.org/pkg/aeguill) This package manages culturally-determined typographical (and other)
          rules for a wide range of languages.
- [babel](https://www.ctan.org/pkg/babel) This package manages culturally-determined typographical (and other) rules
          or a wide range of languages.
- [biblatex](https://www.ctan.org/pkg/biblatex) _BibLaTeX_ is a complete reimplementation of the bibliographic facilities provided by _LaTeX_.
- [csquotes](https://www.ctan.org/pkg/csquotes) This package provides advanced facilities for inline and display quotations.
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
          _LaTeX_ to produce hypertext links in the document.
- [kvoption](https://www.ctan.org/pkg/kvoptions) This package offers support for package authors who want to use options
          in key-value format for their package options.
- [lastpage](https://www.ctan.org/pkg/lastpage) Reference the number of pages in your _LaTeX_ document through the
          introduction of a new label.
- [lmodern](https://www.ctan.org/tex-archive/info/lmodern) Provide some symbol.
- [longtable](https://www.ctan.org/pkg/longtable) Allows writing tables that continue to the next page.
- [minted](https://www.ctan.org/pkg/minted) The package that facilitates expressive syntax highlighting in _LaTeX_ using the powerful _Pygments_ library.
- [multirow](https://www.ctan.org/pkg/multirow) The package has a lot of flexibility, including an option for specifying
          an entry at the “natural” width of its text.
- [tabularx](https://www.ctan.org/pkg/tabularx) The package defines an environment __tabularx__, an extension of
          __tabular__ which has an additional column designator, X, which creates a paragraph-like column whose width automatically
          expands so that the declared width of the environment is filled.
- [titlesec](https://www.ctan.org/pkg/titlesec) A package providing an interface to sectioning commands for selection
          from various title styles.
- [xcolor](https://www.ctan.org/pkg/xcolor) The package starts from the basic facilities of the __color__ package,
          and provides easy driver-independent access.
- [xparse](https://www.ctan.org/pkg/xparse) The package provides a high-level interface for producing document-level commands.

## 3.2. Python

A version of __Python 3.8__ minimum is required. A __requirements.txt__ file will list the different packages needed and their version. To install them easily use the command :

```bash
pip install -r requirements.txt
```
