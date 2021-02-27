from grammar import Grammar, first
import pandas as pd
from pprint import pprint
from abstractsyntaxtree import AbstractSyntaxTree
import random
from constants import *

class LL1Parser(object):
    def __init__(self, fname='ll1-expression-grammar.txt'):
        self.grammar = Grammar(fname)
        self.parsing_table = pd.DataFrame(
            columns=self.grammar.terminals,
            index=self.grammar.nonterminals.keys()
        )
        self.parsing_table.loc[:,:] = ERROR
        self.is_ll1 = True
        pprint(self.parsing_table)
        self.build_parsing_table()

    def build_parsing_table(self):
        for prod in self.grammar.prods:
            lhs, rhs = prod.lhs, prod.rhs
            first_rhs = first(self.grammar, rhs)
            for terminal in first_rhs:
                if terminal is not EPSILON:
                    if self.parsing_table.at[lhs, terminal] == ERROR:
                        self.parsing_table.at[lhs, terminal] = []
                    self.parsing_table.at[lhs, terminal].append(prod)
                else:
                    for symbol in self.grammar.nonterminals[lhs]['follow']:
                        if self.parsing_table.at[lhs, symbol] == ERROR:
                            self.parsing_table.at[lhs, symbol] = []
                        self.parsing_table.at[lhs, symbol].append(prod)
                        if len(self.parsing_table.at[lhs, symbol]) > 1:
                            self.is_ll1 = False
        pprint(self.parsing_table)

    def parse(self, string):
        # string: list of terminals
        if string[-1] != '$':
            string.append('$')
        # stack = ['S\'']
        stack = [AbstractSyntaxTree('S\'')]
        popped_stack = []
        while stack[-1].root != '$':
            # Don't assign, destroys the tree ref
            a = string[0]
            if stack[-1].root == a:
                popped_stack.append(stack.pop(-1))
                a = string.pop(0)
            elif stack[-1].root in self.grammar.terminals:
                raise ValueError('Error because top = {}, terminal'.format(top))
            elif self.parsing_table.at[stack[-1].root, a] == ERROR:
                raise ValueError('Error because parsing table errored out')
            elif self.parsing_table.at[stack[-1].root, a] != ACCEPT:
                prod = self.parsing_table.at[stack[-1].root, a][0]
                stack[-1].prod_id = self.grammar.prods.index(prod)
                print(prod)
                desc_list = []
                for symbol in prod.rhs:
                    x = AbstractSyntaxTree(symbol)
                    stack[-1].desc.append(x)
                    desc_list.append(x)
                popped_stack.append(stack.pop(-1))
                if prod.rhs[0] != EPSILON:
                    for i in range(len(desc_list)-1, -1, -1):
                        stack.append(desc_list[i])
                pprint(list(reversed(stack)))
                print(64*'-')
        return popped_stack[0]
    
    def visualize_syntaxtree(self, string):
        import pygraphviz as pgv
        # Create the parse tree
        tree = self.parse(string)
        if tree.root == 'S\'':
            tree = tree.desc[0]
        G = pgv.AGraph(name='AbstractSyntaxTree', directed=True)
        node_id = 0
        stack = [(tree, node_id)]
        terminals = self.grammar.terminals
        prods = []
        while stack:
            top, node = stack.pop(0)
            if str(node) not in G.nodes():
                G.add_node(node_id, label=top.root)
                node_id += 1
            if top.prod_id is not None:
                color = COLORS[top.prod_id % len(COLORS)]
                G.get_node(node).attr['fontcolor'] = color
            desc_ids = []
            # G.get_node(node).attr['label'] += ', {}'.format(top.prod_id)
            for desc in top.desc:
                if desc.root == EPSILON:
                   label = G.get_node(node).attr['label'] 
                   label = '<' + label + ' = &#x3B5;>'
                   G.get_node(node).attr['label'] = label
                   break
                G.add_node(node_id, label=desc.root)
                G.add_edge(node, node_id, color=color)
                desc_ids.append(node_id)
                stack.append((desc, node_id))
                node_id += 1
            prods.append(desc_ids)

        # Perform a DFS to get proper order of terminals
        terminal_nodes = []
        stack = [G.nodes()[0]]
        visited = []
        while stack:
            node = stack.pop(-1)
            if node not in visited:
                visited.append(node)
                if node.attr['label'] in terminals:
                    terminal_nodes.append(node)
                print(node.attr['label'])
                for i in range(len(G.successors(node))-1, -1, -1):
                    stack.append(G.successors(node)[i])
                # stack.extend(G.successors(node))
        print(terminal_nodes)

        for i, prod in enumerate(prods):
            nonterminals = []
            print(i, prod)
            for node_id in prod:
                if G.get_node(node_id).attr['label'] in terminals:
                    continue
                nonterminals.append(G.get_node(node_id))
            if len(nonterminals) <= 1:
                continue
            nt = G.subgraph(nonterminals, name='Production' + str(i))
            nt.graph_attr['rank'] = 'same'
            for j in range(len(nt.nodes())-1):
                print('Adding edge from c.nodes()[{}]={} to c.nodes()[{}]={}'.format(
                    j, nonterminals[j], j+1, nonterminals[j+1]
                ))
                nt.add_edge(nonterminals[j], nonterminals[j+1], \
                        style='invis', weight=INFINITY)
        
        t = G.add_subgraph(terminal_nodes, name='Terminals')
        t.graph_attr['rank'] = 'max'
        for i in range(len(t.nodes())-1):
            print('Adding edge from c.nodes()[{}]={} to c.nodes()[{}]={}'.format(
                i, terminal_nodes[i], i+1, terminal_nodes[i+1]
            ))
            t.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis')
        

        G.edge_attr['dir'] = 'none'
        G.node_attr['ordering'] = 'out'
        G.node_attr['shape'] = 'none'
        G.node_attr['height'] = 0
        G.node_attr['width'] = 0
        G.node_attr['margin'] = 0.1
        G.layout('dot')

        G.draw('sample.png')
        G.draw('sample.svg')
        return G
        # print(tree)
        # print(G.string())



if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ll1 = LL1Parser(sys.argv[1])
    else:
        ll1 = LL1Parser()
    string = 'id + id * id / id - ( id )'
    string = [x.strip() for x in string.split(' ')]
    ll1.visualize_syntaxtree(string)
