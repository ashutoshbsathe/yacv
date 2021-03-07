---
layout: default
nav_order: 5
title: ManimGL vs ManimCE
---

# ManimGL vs ManimCE

`yacv` is written to be compatible with both [ManimGL - the original manim version by 3b1b](https://github.com/3b1b/manim) and [ManimCE - the community edition](https://github.com/ManimCommunity/manim). However, using ManimCE is recommended for most users. Personally, I could not get ManimGL to render anything above 720p using ManimGL. This could be just me having issue with my OpenGL, your results may vary. ManimCE has always worked perfectly and hence is recommended 

## LL(1) parsing

Grammar: [ll1-expression-grammar](https://github.com/ashutoshbsathe/yacv/blob/main/examples/grammars/ll1-expression-grammar.txt)

String: `id + id * id / id - id`

### ManimGL rendering

<video width="854" height="480" controls>
<source src="../vids/ll1/expr-demo-manimgl.mp4" type="video/mp4">
Your browser does not support video tag
</video>

### ManimCE rendering 

<video width="854" height="480" controls>
<source src="../vids/ll1/expr-demo-manimce.mp4" type="video/mp4">
Your browser does not support video tag
</video>

## LALR(1) parsing

Grammar: [expression-grammar](https://github.com/ashutoshbsathe/yacv/blob/main/examples/grammars/expression-grammar.txt)

String: `id + id * id / id - id`

### ManimGL rendering 

<video width="854" height="480" controls>
<source src="../vids/lalr1/expr-demo-manimgl.mp4" type="video/mp4">
Your browser does not support video tag
</video>

### ManimCE rendering 

<video width="854" height="480" controls>
<source src="../vids/lalr1/expr-demo-manimce.mp4" type="video/mp4">
Your browser does not support video tag
</video>

