---
layout: default
title: Classes
nav_order: 1
parent: Reference
---

# Classes 
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Production
Represents a single production

| Member | Type | Comment |
| ------ | ---- | ------- |
| `lhs` | `str` | LHS of the production |
| `rhs` | `list` | RHS of the production stored as a list |

The class also implements functions for pretty printing and checking equality of 2 productions

File : [grammar.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/grammar.py)

## Grammar
Represents the grammar and stores key information related to it 

| Member | Type | Comment |
| ------ | ---- | ------- |
| `prods` | `list` | List of all productions (each element is an instance of [`Production`](/yacv/reference/classes/#production) class). This list also contains the augmented production $$S' \rightarrow S$$$ at index 0 |
| `terminals` | `list` | List of all terminal symbols in the grammar |
| `nonterminals` | `dict` | Dictionary with every nonterminal in the grammar as keys. For every nonterminal $$X$$, `first` = $$FIRST(X)$$, `follow` = $$FOLLOW(X)$$, `prods_lhs` = list of productions in which $$X$$ appears on LHS, `prods_rhs` = list of productions where $$X$$ appears on RHS |
| `build_first` | `function` | Function that builds $$FIRST(X)$$ for every nonterminal $$X$$ in grammar |
| `build_follow` | `function` | Function that builds $$FOLLOW(X)$$ for every nonterminal $$X$$ in the grammar |

File : [grammar.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/grammar.py)

## AbstractSyntaxTree 
A simple $$n$$-ary class implementation with extra fields for parsing and visualization

| Member | Type | Comment |
| ------ | ---- | ------- |
| `root` | `str` | Root of the tree | 
| `desc` | `list` | List of descendant trees |
| `prod_id` | `int` | What production ID does this AST correspond to ? |
| `node_id` | `int` | Graphviz node ID corresponding to root |


File : [abstractsyntaxtree.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/abstractsyntaxtree.py)

## LL1Parser 
Represents LL(1) parser. Note that currently, the parser can detect only the obvious left recursion (such as $$E \rightarrow E + T$$) but not implied (such as $$A \rightarrow B C$$, $$B \rightarrow A C$$) so please make sure that the grammar used for construction of LL1Parser is valid LL(1)

| Member | Type | Comment |
| ------ | ---- | ------- |
| `grammar` | [`Grammar`](/yacv/reference/classes/#grammar) | Instance of grammar for which the parser is to be built |
| `parsing_table` | [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) | Parsing table for the parser. Each cell in this dataframe will contain either a special value (`YACV_ERROR`/`YACV_ACCEPT`) or list of actions |
| `is_ll1` | `bool` | Boolean which tells whether the grammar is a valid LL(1) grammar or not. This is checked after building the parsing table by looking for cells which have more than one actions in them |
| `build_parsing_table` | `function` | Function that builds LL(1) parsing table using $$FIRST$$ and $$FOLLOW$$ sets. After the parsing table is built, it will also set/unset the `is_ll1` accordingly |
| `parse` | `function` | Takes in a string (list of tokens) and attempts to parse it using the LL(1) parsing table. The function will raise appropriate errors if it fails to parse the string. On successful parsing, the resultant tree will be returned as an [`AbstractSyntaxTree`](/yacv/reference/classes/#abstractsyntaxtree) instance |
| `visualize_syntaxtree` | `function` | Takes in a string (list of tokens) and attempts to visualize the syntax tree generated after parsing. This function relies on `parse` function to parse the string first. If the parsing is successful, the function will convert the generated [`AbstractSyntaxTree`](/yacv/reference/classes#abstractsyntaxtree) into a Graphviz graph and return it |


File : [ll1.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/ll1.py)

## LRItem
Represents a single LR item

| Member | Type | Comment |
| ------ | ---- | ------- |
| `production` | [`Production`](/yacv/reference/classes/#production) | Production corresponding to this item |
| `dot_pos` | `int` | Position of the dot wrt production. `dot_pos=0` corresponds to $$A \rightarrow • B$$ |
| `reduce` | `bool` | Is this item a reduce item ? |
| `update_reduce` | `function` | Update `reduce` based on `dot_pos` and `production` |

File : [lr.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/lr.py)

## LRAutomatonState 
Represents a single state in LR automaton 

| Member | Type | Comment |
| ------ | ---- | ------- |
| `items` | `list` | List of [`LRItem`](/yacv/reference/classes/#lritem)s |
| `preferred_action` | `str` | Preferred action (`'s'` or `'r'`) in case of conflict. Default, `'s'` = SHIFT |
| `shift_items` | `list` | List of items for which next action will be SHIFT |
| `reduce_items` | `list` | List of items for which next action will be REDUCE |
| `accept` | `bool` | Is the current state an accepting state ? Default = `False` |
| `conflict` | `bool` | Does this state have a conflict ? |
| `sr` | `bool` | Does this state have a SHIFT-REDUCE conflict ? |
| `rr` | `bool` | Does this state have a REDUCE-REDUCE conflict ? |
| `update_shift_reduce_items` | `function` | Bifurcate `items` into `shift_items` and `reduce_items` |
| `update_conflicts` | `function` | Update `conflict`, `sr` and `rr` based on `shift_items` and `reduce_items`. Do note that this function is not a litmus test for whether the grammar is valid LR grammar or not. Different parsers will choose to resolve conflicts differently resulting in slightly different parsing tables. Always refer to parsing table for determining whether the given grammar is valid or not |

File : [lr.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/lr.py)

## LRParser

Generic LR parsing class. This is high level implementation of parsing and visualization algorithms. All LR parsing algorithms will inherit this class. Do note that, LR(1) parsers may take significantly longer time for large/ambiguious grammars. It is recommended to use `yacv` for smaller grammars only.

| Member | Type | Comment |
| ------ | ---- | ------- |
| `grammar` | [`Grammar`](/yacv/reference/classes/#grammar) | Grammar for the LR parser |
| `is_valid` | `bool` | Is the given grammar valid under chosen LR parsing algorithm ? |
| `automaton_states` | `list` | List of [`LRAutomatonState`](/yacv/reference/classes/#lrautomatonstate)s which are part of LR automaton of this parser |
| `automaton_transitions` | `dict` | Dictionary describing state transitions for LR automaton |
| `automaton_built` | `bool` | Is the LR automaton ready for this parser ? Default = `False` |
| `parsing_table` | [`pandas.DataFrame`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html) | LR parsing table. Each cell in this dataframe will contain either a special value (`YACV_ERROR`/`YACV_ACCEPT`) or list of actions |
| `closure` | `function` | Takes in a single [`LRItem`](/yacv/reference/classes/#lritem) or list of [`LRItem`](/yacv/reference/classes/#lritem)s and returns their closure as list of [`LRItem`](/yacv/reference/classes/#lritem)s |
| `build_automaton_from_init` | `function` | Takes in the inital [`LRAutomatonState`](/yacv/reference/classes/#lrautomatonstate) and builds the LR automaton from it. After this function is complete `automaton_states` and `automaton_transitions` will be populated properly |
| `parse` | `function` | Takes in a string (list of tokens) and attemps to parse it using the LR parsing table. The function will raise appropriate errors if it fails to parse the string. Do note that, because of the nature of LR parsing, these error messages may not be very intuitive. On successful parsing, an [`AbstractSyntaxTree`](/yacv/reference/classes/#abstractsyntaxtree) corresponding to the parsed string will be returned |
| `visualize_syntaxtree` | `function` | Takes in a string (list of tokens) and attempts to visualize the syntax tree generated after parsing. If the parsing is successful the function will convert the generated [`AbstractSyntaxTree`](/yacv/reference/classes/#abstractsyntaxtree) into a Graphviz graph and return it
| `visualize_automaton` | `function` | Returns a Graphviz graph corresponding to the LR automaton for the parser |

File : [lr.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/lr.py)

## LR0Parser

Inherits [`LRParser`](/yacv/reference/classes/#lrparser)

LR(0) parser uses canonical set of LR(0) items. To create this set, `build_automaton_from_init(x)` is called where $$x = closure([S' \rightarrow • S])$$ where $$S$$ is the starting symbol of the grammar. From this set of items, the LR(0) parsing table is created by `build_parsing_table()`

File : [lr.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/lr.py)

## SLR1Parser

Inherits [`LR0Parser`](/yacv/reference/classes/#lr0parser)

SLR(1) parser uses canonical set of LR(0) items as well. The only difference between SLR(1) parser and LR(0) parser is the method for building the parsing table

File : [lr.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/lr.py)

## LR1Parser 

Inherits [`LRParser`](/yacv/reference/classes/#lrparser)

LR(1) parser or canonical LR(1) parser uses canonical set of LR(1) items. To create this set, `build_automaton_from_init(x)` is called where $$x = closure([S' \rightarrow • S, \$])$$ where $$S$$ is the starting symbol and lookahead $ is represented after "comma". From this set of items, the LR(1) parsing table is created by `build_parsing_table()`


File : [lr.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/lr.py)

## LALR1Parser
Inherits [`LR1Parser`](/yacv/reference/classes/#lr1parser)

LALR(1) parser is implemented by first taking canonical set of LR(1) items and then compacting it by merging together states with common kernel. 

File : [lr.py](https://github.com/ashutoshbsathe/yacv/blob/main/yacv/lr.py)
