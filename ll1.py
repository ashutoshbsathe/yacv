from grammar import Grammar, first, EPSILON
import pandas as pd
from pprint import pprint
from abstractsyntaxtree import AbstractSyntaxTree

ERROR = ''
ACCEPT = 'ACC'
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
        tree = self.parse(string)
        G = pgv.AGraph(directed=True)
        node_id = 0
        stack = [(tree, node_id)]
        while stack:
            top, node = stack.pop(0)
            if str(node) not in G.nodes():
                G.add_node(node_id, label=top.root)
                node_id += 1
            for desc in top.desc:
                if desc.root == EPSILON:
                   label = G.get_node(node).attr['label'] 
                   label = '<' + label + ' = &#x3B5;>'
                   G.get_node(node).attr['label'] = label
                   break
                G.add_node(node_id, label=desc.root)
                G.add_edge(node, node_id)
                stack.append((desc, node_id))
                node_id += 1

        # Perform a DFS to get proper order of terminals
        terminals = self.grammar.terminals
        terminal_nodes = []
        stack = G.nodes()
        visited = []
        while stack:
            node = stack.pop(-1)
            if node not in visited:
                visited.append(node)
                if node.attr['label'] in terminals:
                    terminal_nodes.append(node)
                print(node.attr['label'])
                stack.extend(G.successors(node))
        t = G.add_subgraph(terminal_nodes, name='terminals')
        t.graph_attr['rank'] = 'same'
        for i in range(len(t.nodes())-1):
            print('Adding edge from c.nodes()[{}]={} to c.nodes()[{}]={}'.format(
                i, terminal_nodes[i], i+1, terminal_nodes[i+1]
            ))
            t.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis')
        """
        # How to get proper node order ?
        c = []
        for node_id in terminal_nodes:
            c.append(G.get_node(node_id))
        t = G.add_subgraph(c, name='terminals')
        t.graph_attr['rank'] = 'same'

        for i in range(len(t.nodes())-1):
            print('Adding edge from c.nodes()[{}]={} to c.nodes()[{}]={}'.format(
                i, t.nodes()[i], i+1, t.nodes()[i+1]
            ))
            t.add_edge(t.nodes()[i], t.nodes()[i+1])
        """
        G.layout('dot')
        G.node_attr['shape'] = 'none'
        G.node_attr['height'] = 0
        G.node_attr['width'] = 0
        G.node_attr['margin'] = 0

        G.draw('sample.png')
        print(tree)
        print(G.string())



if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ll1 = LL1Parser(sys.argv[1])
    else:
        ll1 = LL1Parser()
    ll1.visualize_syntaxtree(['id'])
