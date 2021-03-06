---
layout: default
title: Home
nav_order: 1
---

# `yacv`: Yet Another Compiler Visualizer
`yacv` is a tool for visualizing various aspects of typical LL(1) and LR parsers

## Primary features
`yacv` takes in a context free grammar and a string and can be used to :

1. Visualize the syntax tree 
2. Visualize the LR automaton
3. Export the parsing table 
4. Visualize the parsing process step-by-step using [manim](https://github.com/3b1b/manim)

## Working Example

Grammar:

```
S -> C C 
C -> c C 
C -> d 
```

String: `c c d d`

Using the canonical LR(1) parsing method, `yacv` can produce the following:

### Syntax Tree

![ast-simple-cd-grammar](images/ast-simple-cd-grammar.png)

### LR(1) Automaton

![lr1-automata-simple-cd-grammar](images/lr1-automata-simple-cd-grammar.png)

### Canonical LR(1) Parsing Table 

<table>
   <thead>
      <tr>
         <th rowspan="2">STATES</th>
         <th colspan="3">ACTION</th>
         <th colspan="2">GOTO</th>
      </tr>
      <tr>
         <th>$</th>
         <th>c</th>
         <th>d</th>
         <th>S</th>
         <th>C</th>
      </tr>
   </thead>
   <tbody>
      <tr>
         <td>0</td>
         <td>ERR</td>
         <td>['s3']</td>
         <td>['s4']</td>
         <td>['1']</td>
         <td>['2']</td>
      </tr>
      <tr>
         <td>1</td>
         <td>ACC</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
      </tr>
      <tr>
         <td>2</td>
         <td>ERR</td>
         <td>['s6']</td>
         <td>['s7']</td>
         <td>ERR</td>
         <td>['5']</td>
      </tr>
      <tr>
         <td>3</td>
         <td>ERR</td>
         <td>['s3']</td>
         <td>['s4']</td>
         <td>ERR</td>
         <td>['8']</td>
      </tr>
      <tr>
         <td>4</td>
         <td>ERR</td>
         <td>['r3']</td>
         <td>['r3']</td>
         <td>ERR</td>
         <td>ERR</td>
      </tr>
      <tr>
         <td>5</td>
         <td>['r1']</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
      </tr>
      <tr>
         <td>6</td>
         <td>ERR</td>
         <td>['s6']</td>
         <td>['s7']</td>
         <td>ERR</td>
         <td>['9']</td>
      </tr>
      <tr>
         <td>7</td>
         <td>['r3']</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
      </tr>
      <tr>
         <td>8</td>
         <td>ERR</td>
         <td>['r2']</td>
         <td>['r2']</td>
         <td>ERR</td>
         <td>ERR</td>
      </tr>
      <tr>
         <td>9</td>
         <td>['r2']</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
         <td>ERR</td>
      </tr>
   </tbody>
</table>

### Parsing Video 

<video width="854" height="480" controls>
<source src="videos/lr1-vid-simple-cd-grammar.mp4" type="video/mp4">
Your browser does not support video tag
</video>

## Requirements

1. Python 3.6+
2. `pygraphviz`
3. `pandas`
4. `manim` : `yacv` _should_ theoretically work with both manim versions ( [ManimGL](https://github.com/3b1b/manim) or [ManimCE](https://docs.manim.community/en/v0.4.0/installation.html#installing-manim) ) but ManimCE is recommended

# ManimGL vs ManimCE

## LL(1) parsing

Grammar: ll1-expression-grammar

String: id + id * id / id - id 

### ManimGL rendering

<video width="854" height="480" controls>
<source src="videos/ll1/expr-demo-manimgl.mp4" type="video/mp4">
Your browser does not support video tag
</video>

### ManimCE rendering 

<video width="854" height="480" controls>
<source src="videos/ll1/expr-demo-manimce.mp4" type="video/mp4">
Your browser does not support video tag
</video>

## LALR(1) parsing

Grammar: expression-grammar 

String: id + id * id / id - id

### ManimGL rendering 

<video width="854" height="480" controls>
<source src="videos/lalr1/expr-demo-manimgl.mp4" type="video/mp4">
Your browser does not support video tag
</video>

### ManimCE rendering 

<video width="854" height="480" controls>
<source src="videos/lalr1/expr-demo-manimce.mp4" type="video/mp4">
Your browser does not support video tag
</video>
