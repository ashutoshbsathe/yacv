---
layout: default
title: Getting started 
nav_order: 2
---

# Installation

## Requirements

1. Python 3.6+
2. `pygraphviz`
3. `pandas`
4. `manim` : `yacv` _should_ theoretically work with both manim versions ( [ManimGL](https://github.com/3b1b/manim) or [ManimCE](https://docs.manim.community/en/v0.4.0/installation.html#installing-manim) ) but ManimCE is recommended

Issues with `pycairo` ? Check [this](https://github.com/pygobject/pycairo/issues/148#issuecomment-770024652)

To install `yacv`, clone the [`yacv` repository on GitHub](https://github.com/ashutoshbsathe/yacv) to your local machine and then install using pip

```bash
$ git clone https://github.com/ashutoshbsathe/yacv 
$ cd yacv 
$ pip install -e .
```

# Using `yacv`

`yacv` needs a path to config file to work properly. To verify the installation, while in the directory where you cloned the `yacv` repo, run the following:

```bash
$ yacv example_config.yml
```

This should start visualizing LL(1) parsing for a [very simple LL(1) grammar](https://github.com/ashutoshbsathe/yacv/blob/main/examples/grammars/ll1-simple.txt)

If everything run successfully, you should see a new folder named `yacv_ll1-simple/` in your directory. Explore this folder to examine the output

To use `yacv` with your own grammar and string, simply write down your [grammar](/yacv/grammar) rules in a text file and use that to create a new [config](/yacv/config) for `yacv`. Then you can pass path to this config to `yacv` to get your visualizations

Also check out [`examples/`](https://github.com/ashutoshbsathe/yacv/tree/main/examples) directory for more such example configs

