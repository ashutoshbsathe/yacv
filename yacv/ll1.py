import logging 
import pandas as pd
from pprint import pprint
from yacv.grammar import Grammar, first
from yacv.abstractsyntaxtree import AbstractSyntaxTree
from yacv.utils import YACVError 
from yacv.constants import *
class LL1Parser(object):
    def __init__(self, fname='ll1-expression-grammar.txt'):
        self.grammar = Grammar(fname)
        # Check for left recursion
        for prod in self.grammar.prods:
            if prod.lhs == prod.rhs[0]:
                raise YACVError('The grammar is not LL(1) due to left recursion in production {}'.format(prod))

        self.parsing_table = pd.DataFrame(
            columns=self.grammar.terminals,
            index=self.grammar.nonterminals.keys()
        )
        self.parsing_table.loc[:,:] = YACV_ERROR
        self.is_ll1 = True
        # pprint(self.parsing_table)
        self.build_parsing_table()

    def build_parsing_table(self):
        for prod in self.grammar.prods:
            lhs, rhs = prod.lhs, prod.rhs
            first_rhs = first(self.grammar, rhs)
            for terminal in first_rhs:
                if terminal is not YACV_EPSILON:
                    if self.parsing_table.at[lhs, terminal] == YACV_ERROR:
                        self.parsing_table.at[lhs, terminal] = []
                    self.parsing_table.at[lhs, terminal].append(prod)
                else:
                    for symbol in self.grammar.nonterminals[lhs]['follow']:
                        if self.parsing_table.at[lhs, symbol] == YACV_ERROR:
                            self.parsing_table.at[lhs, symbol] = []
                        self.parsing_table.at[lhs, symbol].append(prod)
                        if len(self.parsing_table.at[lhs, symbol]) > 1:
                            self.is_ll1 = False
        if self.is_ll1:
            logging.getLogger('yacv').info('LL(1) parsing table successfully generated')
        else:
            logging.getLogger('yacv').warning('Grammar is not LL(1). 2 or more entries present in at least one cell in parsing table')

    def parse(self, string):
        log = logging.getLogger('yacv')
        if not self.is_ll1:
            raise YACVError('Grammar is not LL(1). The parsing cannot proceed')
        # string: list of terminals
        if string[-1] != '$':
            string.append('$')
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
            elif self.parsing_table.at[stack[-1].root, a] == YACV_ERROR:
                raise ValueError('Error because parsing table errored out')
            elif self.parsing_table.at[stack[-1].root, a] != YACV_ACCEPT:
                prod = self.parsing_table.at[stack[-1].root, a][0]
                stack[-1].prod_id = self.grammar.prods.index(prod)
                log.debug('Expanding production : {}'.format(prod))
                desc_list = []
                for symbol in prod.rhs:
                    x = AbstractSyntaxTree(symbol)
                    stack[-1].desc.append(x)
                    desc_list.append(x)
                popped_stack.append(stack.pop(-1))
                if prod.rhs[0] != YACV_EPSILON:
                    for i in range(len(desc_list)-1, -1, -1):
                        stack.append(desc_list[i])
                log.debug(list(reversed(stack)))
                log.debug('End of iteration' + 16*'-')
        return popped_stack[0]
    
    def visualize_syntaxtree(self, string):
        log = logging.getLogger('yacv')
        import pygraphviz as pgv
        # Create the parse tree
        tree = self.parse(string)
        log.info('String successfully parsed')
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
                color = YACV_GRAPHVIZ_COLORS[top.prod_id % len(YACV_GRAPHVIZ_COLORS)]
                G.get_node(node).attr['fontcolor'] = color
            desc_ids = []
            for desc in top.desc:
                if desc.root == YACV_EPSILON:
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
                for i in range(len(G.successors(node))-1, -1, -1):
                    stack.append(G.successors(node)[i])
                # stack.extend(G.successors(node))
        log.debug('Terminal nodes : {}'.format(terminal_nodes))
        for i, prod in enumerate(prods):
            nonterminals = []
            for node_id in prod:
                if G.get_node(node_id).attr['label'] in terminals:
                    continue
                nonterminals.append(G.get_node(node_id))
            if len(nonterminals) <= 1:
                continue
            nt = G.subgraph(nonterminals, name='Production' + str(i))
            nt.graph_attr['rank'] = 'same'
            for j in range(len(nt.nodes())-1):
                log.debug('Adding edge from c.nodes()[{}]={} to c.nodes()[{}]={}'.format(
                    j, nonterminals[j], j+1, nonterminals[j+1]
                ))
                nt.add_edge(nonterminals[j], nonterminals[j+1], \
                        style='invis', weight=YACV_GRAPHVIZ_INFINITY)
        
        t = G.add_subgraph(terminal_nodes, name='Terminals')
        t.graph_attr['rank'] = 'max'
        for i in range(len(t.nodes())-1):
            log.debug('Adding edge from c.nodes()[{}]={} to c.nodes()[{}]={}'.format(
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

        log.info('Parse tree successfully visualized')
        return G



if __name__ == '__main__':
    from utils import setup_logger
    import sys
    setup_logger()
    if len(sys.argv) > 1:
        ll1 = LL1Parser(sys.argv[1])
    else:
        ll1 = LL1Parser()
    string = 'id + id * id / id - ( id )'
    string = [x.strip() for x in string.split(' ')]
    ll1.visualize_syntaxtree(string)
