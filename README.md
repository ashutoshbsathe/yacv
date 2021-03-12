# yacv: Yet Another Compiler Visualizer

`yacv` is a tool for visualizing various aspects of typical LL(1) and LR parsers. Check out [demo on YouTube](https://www.youtube.com/watch?v=BozB0O0__Qg) to see sample visualizations

## Introduction

Getting comfortable with parsing can be tough. While the legendary ["Dragon Book"](https://suif.stanford.edu/dragonbook/) is an excellent resource for everything related to compilers, it still contains very minimal visualizations for the parsing process itself. That being said, there exist visualization tools such as [LR(0) parser visualizer](https://www.cs.princeton.edu/courses/archive/spring20/cos320/LR0/) and [LL(1) parser visualizer](https://www.cs.princeton.edu/courses/archive/spring20/cos320/LL1/) by Zak Kincaid and Shaowei Zhu, [JSMachines](http://jsmachines.sourceforge.net/machines/lr1.html), [Jison](https://zaa.ch/jison/try/usf/) etc. However, all of these tools are web-based and most of them show steps in a table which isn't very intuitive

`yacv` attempts to overcome all these shortcomings by using [`manim`](https://github.com/3b1b/manim) 

## Primary features
`yacv` takes in a context free grammar and a string and can be used to :

1. Visualize the syntax tree 
2. Visualize the LR automaton
3. Export the parsing table 
4. Visualize the parsing process step-by-step using [manim](https://github.com/3b1b/manim)


## Installation 

Requirements:
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

Check extra notes for install on Ubuntu WSL in the [docs](https://ashutoshbsathe.github.io/yacv/getting-started/#notes-for-ubuntu-wsl)
## Usage 
To verify installation, run `yacv` with the example configuration [`example_config.yml`](example_config.yml)

```bash 
$ yacv example_config.yml 
```

To run with your own grammar and string, create your own custom config and use that instead. Examples of config files with various grammars can be found in [examples/](examples) directory

## Documentation
For more information, please refer to the [documentation](https://ashutoshbsathe.github.io/yacv)

## License
MIT

## Interesting Reads 
1. [A good, free book for interpreters](http://craftinginterpreters.com/)
2. [GCC does not use machine generated parsers](https://stackoverflow.com/questions/6319086/are-gcc-and-clang-parsers-really-handwritten)
3. [Why LL and LR parsing is hard ?](https://blog.reverberate.org/2013/09/ll-and-lr-in-context-why-parsing-tools.html)
