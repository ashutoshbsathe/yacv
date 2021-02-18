from grammar import Grammar, first, EPSILON
from abstractsyntaxtree import AbstractSyntaxTree
from pprint import pprint
from copy import deepcopy
from collections import OrderedDict
import pandas as pd

ACTION = 'ACTION'
ACCEPT = 'ACC'
ERROR  = ''
GOTO   = 'GOTO'
DOT    = '•'
REDUCE = 'r'
SHIFT  = 's'
INFINITY = 2048
COLORS = [
    'coral',
    'darkmagenta',
    'darkblue',
    'darkred',
    'deeppink',
    'dodgerblue',
    'blueviolet',
    'darkcyan',
    'deepskyblue',
    'mediumslateblue',
    'brown',
    'orange',
    'teal',
    'seagreen',
    'springgreen',
    'tomato'
]

class LRItem(object):
    def __init__(self, production=None, dot_pos=0, lookaheads=[]):
        self.production = production
        self.dot_pos = dot_pos
        self.lookaheads = lookaheads
        self.update_reduce()

    def update_reduce(self):
        if self.dot_pos == len(self.production.rhs) \
        or self.production.rhs[self.dot_pos] in ['$', EPSILON]:
            self.reduce = True
        else:
            self.reduce = False

    def __str__(self):
        # TODO: Some string format customization maybe ?
        lhs, rhs = self.production.lhs, self.production.rhs
        lookaheads = sorted(self.lookaheads)
        dot_pos = self.dot_pos
        ret = '{} -> {}{}{}'.format(
                lhs,
                ''.join(rhs[:dot_pos]) if dot_pos > 0 else '',
                DOT,
                ''.join(rhs[dot_pos:])
                )
        if lookaheads:
            ret += ', {}'.format('/'.join(lookaheads))
        return ret

    def __repr__(self):
        return '< ' + str(self) + ' > at {}'.format(hex(id(self)))
    
    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return not self == other

class LRAutomatonState(object):
    def __init__(self, items=[], preferred_action='S'):
        self.items = items
        self.preferred_action = preferred_action
        self.shift_items = []
        self.reduce_items = []
        self.accept = False # is accepting state ?
        self.update_shift_reduce_items()
        self.update_conflicts()

    def update_shift_reduce_items(self):
        for i, item in enumerate(self.items):
            item.update_reduce()
            if item.reduce:
                self.reduce_items.append(i)
                if item.production.rhs[-1] == '$':
                    self.accept = True
            else:
                self.shift_items.append(i)

    def update_conflicts(self):
        if len(self.reduce_items) > 1:
            # Reduce Reduce conflict
            self.rr = True
            self.conflict = True
        if len(self.reduce_items) > 1 and len(self.shift_items) > 1:
            # Shift Reduce conflict
            self.sr = True
            self.conflict = True

    def __str__(self, join_on='\n'):
        # TODO: Can provide some customization here
        return join_on.join([str(item) for item in self.items])

    def __repr__(self):
        return '< LRAutomatonState with items: ' + str(self) + \
                ' > at {}'.format(hex(id(self)))

    def __eq__(self, other):
        return self.items == other.items

    def __ne__(self, other):
        return not self == other

class LRParser(object):
    def __init__(self, fname='another-grammar.txt'):
        self.grammar = Grammar(fname)
        self.is_valid = True
        self.automaton_states = []
        self.automaton_transitions = OrderedDict()
        self.automaton_built = False
        self.build_automaton()
        tuples = [(ACTION, symbol) for symbol in self.grammar.terminals] + \
            [(GOTO, symbol) for symbol in self.grammar.nonterminals.keys()]
        columns = pd.MultiIndex.from_tuples([('', x[0])
            if pd.isnull(x[1]) else x for x in tuples])
        self.parsing_table = pd.DataFrame(
            columns = columns,
            index = self.automaton_transitions.keys()
        )
        self.parsing_table.loc[:,:] = ERROR
        self.parsing_table_built = False
        self.build_parsing_table()

    def closure(self, i):
        queue = i if isinstance(i, list) else [i]
        ret = []
        print('Computing closure of {}'.format(queue))
        while queue:
            item = queue.pop(0)
            assert isinstance(item, LRItem)
            ret.append(item)
            print('item = {}, reduce = {}'.format(item, item.reduce))
            if item.reduce:
                continue
            next_symbol = item.production.rhs[item.dot_pos]
            print('next_symbol = {}'.format(next_symbol))
            if next_symbol == EPSILON \
            or next_symbol in self.grammar.terminals:
                continue
            prod_ids = self.grammar.nonterminals[next_symbol]['prods_lhs']
            print('new_prod_ids = {}'.format(prod_ids))
            for prod_id in prod_ids:
                prod = self.grammar.prods[prod_id]
                print(type(item.lookaheads))
                if item.lookaheads:
                    f = first(self.grammar, 
                            item.production.rhs[item.dot_pos+1:])
                    if EPSILON not in f:
                        f = f.union(set(item.lookaheads).difference(['$']))
                    else:
                        f = f.union(set(item.lookaheads))
                    f = f.difference([EPSILON])
                else:
                    f = []
                new_item = LRItem(prod, 0, f)
                print('new_item = {}'.format(new_item))
                if new_item not in queue and new_item not in ret:
                    queue.append(new_item)
        kernel_lookaheads = OrderedDict()
        for item in ret:
            kernel = LRItem(item.production, item.dot_pos)
            key = str(kernel)
            if key not in kernel_lookaheads.keys():
                kernel_lookaheads[key] = {
                    'kernel': kernel,
                    'lookaheads': []
                }
            curr = kernel_lookaheads[key]['lookaheads']
            curr = sorted(list(set(curr).union(item.lookaheads)))
            kernel_lookaheads[key]['lookaheads'] = curr
        ret = []
        for key, val in kernel_lookaheads.items():
            kernel, lookaheads = val['kernel'], val['lookaheads']
            item = LRItem(kernel.production, kernel.dot_pos, lookaheads)
            ret.append(item)
        return ret

    def build_automaton_from_init(self, init):
        if self.automaton_built:
            # TODO: raise a warning here
            return
        # init = LRAutomatonState(self.closure(LRItem(self.grammar.prods[0], 0)))
        self.automaton_states.append(init)
        self.automaton_transitions[0] = OrderedDict()
        visited_states = []
        to_visit = [init]
        while to_visit:
            curr = to_visit.pop(0)
            curr_idx = self.automaton_states.index(curr)
            print('curr = {}'.format(curr))
            visited_states.append(curr)
            tmp_items = deepcopy(curr.items)
            next_symbols = OrderedDict()
            for item in tmp_items:
                if item.reduce:
                    continue
                key = item.production.rhs[item.dot_pos]
                if key not in next_symbols.keys():
                    next_symbols[key] = []
                item.dot_pos += 1
                item.update_reduce()
                next_symbols[key].append(item)
            pprint(next_symbols)
            for key, items in next_symbols.items():
                next_state = LRAutomatonState(self.closure(items))
                print(next_state)
                if next_state not in self.automaton_states:
                    # Is next_state completely new ?
                    print('Adding new state {}'.format(next_state))
                    self.automaton_states.append(next_state)
                    self.automaton_transitions[len(self.automaton_states)-1] = \
                        OrderedDict()
                    to_visit.append(next_state)
                elif next_state not in visited_states:
                    # next_state is not new but is not visited either
                    to_visit.append(next_state)
                else:
                    # next_state already exists and is visited
                    print('State {} is already visited'.format(next_state))
                next_idx = self.automaton_states.index(next_state)
                self.automaton_transitions[curr_idx][key] = next_idx
                print(32 * '-')
            print(64*'-')
        print('to_visit = empty')
        self.automaton_built = True

    def build_parsing_table(self):
        pass

    def parse(self, string):
        # page 7 at below link is really helpful
        # https://www2.cs.duke.edu/courses/spring02/cps140/lects/sectlrparseS.pdf
        assert self.parsing_table_built
        assert len(string) > 0
        terminals = self.grammar.terminals
        if string[-1] != '$':
            string.append('$')
        stack = [0]
        last_popped = None
        while True:
            top = stack[-1]
            a = string[0]
            entry = self.parsing_table.at[top, (ACTION, a)]
            if entry == ERROR:
                print('Parse error')
                raise ValueError()
            if isinstance(entry, list):
                entry = entry[0]
            print('stack top = {}, a = {}, entry = {}'.format(top, a, entry))
            if entry[0] == 's':
                stack.append(AbstractSyntaxTree(a))
                stack.append(int(entry[1:]))
                string.pop(0)
            elif entry[0] == 'r':
                prod_id =int(entry[1:])
                prod = self.grammar.prods[prod_id]
                new_tree = AbstractSyntaxTree(prod.lhs)
                new_tree.prod_id = prod_id
                # the curr_nonterminals part is janky asf
                # think if we can put the tree in the stack itself
                """
                for i, symbol in enumerate(prod.rhs):
                    if symbol not in terminals and symbol != EPSILON:
                        # i must be nonterminal
                        new_tree.desc[i] = curr_nonterminals[symbol][0]
                        curr_nonterminals[symbol].pop(0)
                """
                popped_list = []
                for _ in range(len(prod.rhs)):
                    if not stack:
                        raise ValueError()
                    stack.pop(-1) # pops the state number
                    if not stack:
                        raise ValueError()
                    popped_list.append(stack.pop(-1)) # pops the symbol
                last_popped = popped_list[-1]
                for i in range(len(popped_list)-1, -1, -1):
                    new_tree.desc.append(popped_list[i])
                new_top = stack[-1]
                nonterminal = prod.lhs
                new_state = self.parsing_table.at[new_top, (GOTO, nonterminal)]
                stack.append(new_tree)
                if isinstance(new_state, list):
                    new_state = new_state[0]
                stack.append(int(new_state))
            elif entry == ACCEPT:
                prod = self.grammar.prods[0]
                assert prod.rhs[-1] == '$' and len(prod.rhs) == 2
                if not stack:
                    raise ValueError() # Not sure if we need this here
                stack.pop(-1)
                if not stack:
                    raise ValueError() # Not sure if we need this here
                tree = stack.pop(-1)
                print('Parse successful')
                print('Final tree = {}'.format(tree))
                return tree
                break
            else:
                print('Unknown Error')
                break
            print(stack)
            print(string)
            print(64 *'-')

    def visualize_syntaxtree(self, string):
        import pygraphviz as pgv
        # Create the parse tree
        tree = self.parse(string)

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
            pprint(top.desc)
            for desc in top.desc:
                pprint(desc)
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

    def visualize_automaton(self):
        import pygraphviz as pgv
        G = pgv.AGraph(rankdir='LR', directed=True)
        G.add_node(-1, style='invis')
        for i, state in enumerate(self.automaton_states):
            label = '<U><B>State {}<BR/></B></U>'.format(i) + \
                    state.__str__(join_on='<BR/>') 
            label = label.replace(DOT, '&#xB7;')
            label = label.replace('->', '&#10132;')
            label = '<' + label + '>'
            print(label)
            if len(state.reduce_items) > 0:
                # This is a reduce state
                fillcolor = '#90EE90' if state.accept else '#85CAF6'
                G.add_node(i, label=label, peripheries=2, 
                            style='filled', fillcolor=fillcolor)
                print('Added reduce node')
            else:
                G.add_node(i, label=label)
                print('Added node')
            print(64*'-')
        G.add_edge(-1, 0)
        for state, transitions in self.automaton_transitions.items():
            for symbol, new_state in transitions.items():
                G.add_edge(state, new_state, label=symbol)

        G.write('sample.dot')
        G.node_attr['shape'] = 'box'
        G.node_attr['height'] = 0
        G.node_attr['width'] = 0
        G.node_attr['margin'] = 0.05
        G.layout('dot')
        G.draw('sample.png')

class LR0Parser(LRParser):
    # TODO: Can we support epsilon LR(0) parsers ?
    # Ref: Parsing Techniques - Practical Guide 2nd Edition Sec.9.5.4
    def build_automaton(self):
        if self.automaton_built:
            # TODO: Warn user
            return
        init = LRAutomatonState(self.closure(LRItem(self.grammar.prods[0], 0)))
        self.build_automaton_from_init(init)

    def build_parsing_table(self):
        # TODO: Silently return if parsing table is built ?
        assert self.automaton_built
        terminals = self.grammar.terminals
        for state_id, transitions in self.automaton_transitions.items():
            state = self.automaton_states[state_id]
            if state.accept:
                col = (ACTION, '$')
                self.parsing_table.at[state_id, col] = ACCEPT
            elif len(state.reduce_items) > 0:
                for t in self.grammar.terminals:
                    col = (ACTION, t)
                    if self.parsing_table.at[state_id, col] == ERROR:
                        self.parsing_table.at[state_id, col] = []
                    for item in state.items:
                        if item.reduce:
                            prod_id = self.grammar.prods.index(item.production)
                            entry = REDUCE + str(prod_id)
                            self.parsing_table.at[state_id, col].append(entry)
                            if len(self.parsing_table.at[state_id, col]) > 1:
                                self.is_valid = False
            for symbol, new_state_id in transitions.items():
                if symbol in terminals:
                    entry = SHIFT + str(new_state_id)
                    col = (ACTION, symbol)
                else:
                    entry = str(new_state_id)
                    col = (GOTO, symbol)
                if self.parsing_table.at[state_id, col] == ERROR:
                    self.parsing_table.at[state_id, col] = []
                self.parsing_table.at[state_id, col].append(entry)
                if len(self.parsing_table.at[state_id, col]) > 1:
                    self.is_valid = False

        pprint(self.parsing_table)
        print(self.is_valid)
        self.parsing_table_built = True

class SLR1Parser(LR0Parser):
    def build_parsing_table(self):
        # TODO: Silently return if parsing table is built ?
        assert self.automaton_built
        terminals = self.grammar.terminals
        for state_id, transitions in self.automaton_transitions.items():
            state = self.automaton_states[state_id]
            if state.accept:
                col = (ACTION, '$')
                self.parsing_table.at[state_id, col] = ACCEPT
            elif len(state.reduce_items) > 0:
                for item in state.items:
                    if item.reduce:
                        lhs = item.production.lhs
                        follow = self.grammar.nonterminals[lhs]['follow']
                        prod_id = self.grammar.prods.index(item.production)
                        entry = REDUCE + str(prod_id)
                        for symbol in follow:
                            col = (ACTION, symbol)
                            if self.parsing_table.at[state_id, col] == ERROR:
                                self.parsing_table.at[state_id, col] = []
                            self.parsing_table.at[state_id, col].append(entry)
                            if len(self.parsing_table.at[state_id, col]) > 1:
                                self.is_valid = False
            for symbol, new_state_id in transitions.items():
                if symbol in terminals:
                    entry = SHIFT + str(new_state_id)
                    col = (ACTION, symbol)
                else:
                    entry = str(new_state_id)
                    col = (GOTO, symbol)
                if self.parsing_table.at[state_id, col] == ERROR:
                    self.parsing_table.at[state_id, col] = []
                self.parsing_table.at[state_id, col].append(entry)
                if len(self.parsing_table.at[state_id, col]) > 1:
                    self.is_valid = False

        pprint(self.parsing_table)
        print(self.is_valid)
        self.parsing_table_built = True

class LR1Parser(LRParser): 
    def build_automaton(self):
        if self.automaton_built:
            # TODO: Warn user
            return
        init = LRAutomatonState(self.closure(LRItem(
            self.grammar.prods[0], 0, ['$'])))
        self.build_automaton_from_init(init)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        #lr0 = LR0Parser(sys.argv[1])
        p = LR0Parser(sys.argv[1])
    else:
        #lr0 = LR0Parser()
        p = LR0Parser()
    p.visualize_automaton()
    p.visualize_syntaxtree(['c', 'd', 'd'])
    
