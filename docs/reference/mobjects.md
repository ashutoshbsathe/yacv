---
layout: default
title: Mobjects
nav_order: 2
parent: Reference
---

# Mobjects
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## GraphvizMobject

Inherits [manim.mobject.types.vectorized\_mobject.VGroup](https://docs.manim.community/en/v0.4.0/reference/manim.mobject.types.vectorized_mobject.VGroup.html?#manim.mobject.types.vectorized_mobject.VGroup)

This is used to put any Graphviz graph into `manim`. The Graphviz graph must be already laid out before it can be added as a `manim` VGroup. The bounding box information present in the Graphviz graph will be used to adjust it's size and location on `manim`'s 14x8 grid

The VGroup also stores node ID and edge ID for each node and edge in the graph which makes it easier for animating

File : [mobjects.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/mobjects.py)
## StackMobject

Inherits [manim.mobject.types.vectorized\_mobject.VGroup](https://docs.manim.community/en/v0.4.0/reference/manim.mobject.types.vectorized_mobject.VGroup.html?#manim.mobject.types.vectorized_mobject.VGroup)

This is used to show stack elements. The constant `YACV_MANIM_STACK_VIS` controls how many elements at max must be visible in the stack. If more elements are present, the stack bottom becomes a dotted line to indicate more items

## LL1ParsingVisualizer

Inhertis [manim.scene.scene.Scene](https://docs.manim.community/en/v0.4.0/reference/manim.scene.scene.Scene.html#manim.scene.scene.Scene)

Main scene for LL(1) parsing. This scene is effectively a reimplementation of `parse()` from [`LL1Parser`](/yacv/reference/classes/#ll1parser) but it also animates the [`GraphvizMobject`](/yacv/reference/mobjects/#graphvizmobject) and [`StackMobject`](/yacv/reference/mobjects/#stackmobject) after every step. Like the usual `parse()`, this scene will also raise errors in case the parsing is unsuccessful

Currently, `yacv` can visualize only valid strings in a grammar


File : [vis.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/vis.py)
## LRParsingVisualizer

Inhertis [manim.scene.scene.Scene](https://docs.manim.community/en/v0.4.0/reference/manim.scene.scene.Scene.html#manim.scene.scene.Scene)

Like [`LL1ParsingVisualizer`](/yacv/reference/mobjects/#ll1parsingvisualizer) but for LR parsing

File : [mobjects.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/mobjects.py)
