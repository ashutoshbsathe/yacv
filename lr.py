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
        assert self.parsing_table_built
        assert len(string) > 0
        terminals = self.grammar.terminals
        if string[-1] != '$':
            string.append('$')
        stack = [0]
        curr_nonterminals = OrderedDict()
        while True:
            top = stack[-1]
            a = string[0]
            entry = self.parsing_table.at[top, (ACTION, a)]
            if isinstance(entry, list):
                entry = entry[0]
            print('stack top = {}, a = {}, entry = {}'.format(top, a, entry))
            if entry[0] == 's':
                stack.append(a)
                stack.append(int(entry[1:]))
                string.pop(0)
            elif entry[0] == 'r':
                prod_id =int(entry[1:])
                prod = self.grammar.prods[prod_id]
                new_tree = AbstractSyntaxTree(prod)
                new_tree.prod_id = prod_id
                num_pops = 0
                for i, symbol in enumerate(prod.rhs):
                    if symbol in terminals:
                        num_pops += 1
                    elif symbol != EPSILON:
                        # i must be nonterminal
                        new_tree.desc[i] = curr_nonterminals[symbol][0]
                        curr_nonterminals[symbol].pop(0)
                for _ in range(num_pops):
                    if not stack:
                        raise ValueError
                    stack.pop(-1)
                    if not stack:
                        raise ValueError
                    stack.pop(-1)
                if not stack:
                    raise ValueError
                new_top = stack.pop(-1)
                nonterm = prod.lhs
                new_state = self.parsing_table.at[new_top, (GOTO, nonterm)]
                if isinstance(new_state, list):
                    new_state = int(new_state[0])
                stack.append(new_state)
                print(prod)
                if prod.lhs not in curr_nonterminals:
                    curr_nonterminals[prod.lhs] = []
                curr_nonterminals[prod.lhs].append(new_tree)
            elif entry == ACCEPT:
                prod = self.grammar.prods[0]
                assert prod.rhs[-1] == '$' and len(prod.rhs) == 2
                tree = AbstractSyntaxTree(prod)
                tree.desc[0] = curr_nonterminals[prod.rhs[0]]
                print('Parse successful')
                print('Final tree = {}'.format(tree))
                return tree
                break
            elif entry == ERROR:
                print('Parsing Error')
                break
            else:
                print('Unknown Error')
                break
            print(stack)
            print(string)
            print(curr_nonterminals)

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
        p = SLR1Parser(sys.argv[1])
    else:
        #lr0 = LR0Parser()
        p = SLR1Parser()
    p.parse(['a', 'a', 'a', 'b', 'b', 'b'])
    
