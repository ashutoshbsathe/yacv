---
layout: default
title: Grammar specification
nav_order: 4
---

# Grammar specification

`yacv` expects a context free grammar $$G = (V, T, P, S)$$

Here,
* $$V$$ : set of variable/non-terminal symbols 
* $$T$$ : set of terminal symbols 
* $$P$$ : list of productions
* $$S$$ : starting symbol

`yacv` expects a text file with list of productions. Each production $$A \rightarrow B$$ such that $$A \in V$$, $$B \in (V+T)^*$$ should be written as :

```
A -> B
```

Important notes :
* Each symbol in $$B$$ must be separated by a whitespace
* The grammar file is expected to contain only the list of productions
* `yacv` will assume all the symbols that appear on the LHS of the production to be nonterminals
* Any symbol that is not a nonterminal will be considered as a terminal 
* LHS of the very first production in grammar file will be assumed as starting symbol 
* To indicate $$\epsilon$$, `''` must be used. Therefore, production $$S \rightarrow \epsilon$$ must be written as `S -> ''`
* Symbol $ is reserved as an end of string and must not occur anywhere in the grammar file
* Symbol `S'` is reserved for the augmented production [$$S' \rightarrow S$$ $]. This augmented production is automatically added by the parser so you need not add it yourself

<table>
<thead>
<tr>
<th> Example CFG </th>
<th> CFG in <code>yacv</code> readable format </th>
</tr>
</thead>
<tr>
<td>
$$ S \rightarrow a S b \;|\; \epsilon $$
</td>
<td>
<pre>
S -> a S b 
S -> ''
</pre>
</td>
</tr>

<tr>
<td>
$$ 
\begin{aligned}
STMT &\rightarrow \verb+if+ \; STMT \; \verb+else+ \; STMT \\
     & |\; \verb+if+ \; STMT \;|\; a \;|\; b \;|\; c \;|\; d
\end{aligned}
$$
</td>
<td>
<pre>
STMT -> if STMT else STMT
STMT -> if STMT
STMT -> a
STMT -> b
STMT -> c
STMT -> d
</pre>
</td>
</tr>


<tr>
<td>
$$ 
\begin{aligned}
E &\rightarrow E + T \;|\; E - T \;|\; T\\
T &\rightarrow T * F \;|\; T / F \;|\; F\\
F &\rightarrow ( E ) \;|\; id 
\end{aligned}
$$
</td>
<td>
<pre>
E -> E + T
E -> E - T
E -> T
T -> T * F
T -> T / F
T -> F
F -> ( E )
F -> id
</pre>
</td>
</tr>
</table>
