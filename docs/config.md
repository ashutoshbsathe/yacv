---
layout: default
title: Configuration file
nav_order: 3
---

# Configuration file 

The config file is a YAML file with following attributes:

1. `grammar`: (must be specified) Path to grammar file. Refer to [grammar spec](/yacv/grammar) for more info grammar file
2. `string`: (must be specified) The string to be parsed. The string must contain space separated tokens. For example, with [expression grammar](https://github.com/ashutoshbsathe/yacv/blob/main/examples/grammars/expression-grammar.txt), string `id + id` is valid whereas `id+id` is not valid for `yacv`
3. `parsing-algo`: (must be specified) Parsing algorithm to be used for parsing. The valid choices are [`ll1`, `lr0`, `slr1`, `lr1`, `lalr1`]
4. `vis-tree`: (default `False`) Boolean which controls the visualization of the resultant syntaxtree. The syntaxtree will be exported to a PDF file if this option is set 
5. `vis-automaton`: (default `False`) Boolean which controls the visualization of LR automaton. Naturally this is valid only when `parsing-algo` is some LR parser. The automaton will be exported to a PDF file if this option is set 
6. `parsing-table`: (default `False`) Boolean which saves the parsing table to a `.csv` file. This can be useful for debugging a grammar which is not valid for a particular parsing algorithm. Parsing table exported by this option will have a list of actions to be performed at each entry. For a valid grammar and parsing algorithm, each list will contain at most one action or an error entry.
7. `vis-parsing`: (default `False`) Boolean which controls the step-by-step visualization of parsing procedure. The animation is done via [`manim`](https://github.com/3b1b/manim) and a `.mp4` file is exported 
8. `manim-video-quality`: (default `480p`) Controls the quality of manim export. Valid choices are [`480p`, `720p`, `1080p`, `1440p`, `2160p`]

Optionally, you may specify custom colors that will be used for coloring productions in visualizations. This can be specified as a list attribute `colors` in the configuration file

When visualizing, color of production $$i$$ (indexing based on the line number in the grammar file) is determined as $$color[i] = colors[i \mod len(colors)]$$. Do note that the same color is used for syntax tree visualization as well as steo-by-step (manim) visualization. Default colors are specified in [`constants.py`](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/constants.py)
