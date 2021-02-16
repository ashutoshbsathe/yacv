from grammar import Grammar, first, EPSILON
from pprint import pprint
from copy import deepcopy
from collections import OrderedDict
import pandas as pd

ACTION = 'ACTION'
ACCEPT = 'ACC'
ERROR  = ''
GOTO   = 'GOTO'

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
        ret = '{} -> {}•{}'.format(
                lhs,
                ''.join(rhs[:dot_pos]) if dot_pos > 0 else '',
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
        self.update_shift_reduce_items()
        self.update_conflicts()

    def update_shift_reduce_items(self):
        for i, item in enumerate(self.items):
            item.update_reduce()
            if item.reduce:
                self.reduce_items.append(i)
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

    def __str__(self):
        # TODO: Can provide some customization here
        return '\\n'.join([str(item) for item in self.items])

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
                            item.production.rhs[item.dot_pos+1:] +\
                            list(item.lookaheads))
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

    def visualize_automaton(self):
        import pygraphviz as pgv
        G = pgv.AGraph(rankdir='LR', directed=True)
        G.add_node(-1, style='invis')
        for i, state in enumerate(self.automaton_states):
            G.add_node(i, label='State {}\\n\\n'.format(i) + str(state))
        G.add_edge(-1, 0)
        for state, transitions in self.automaton_transitions.items():
            for symbol, new_state in transitions.items():
                G.add_edge(state, new_state, label=symbol)

        G.layout('dot')
        G.node_attr['shape'] = 'box'
        G.draw('sample.png')
        G.write('sample.dot')

class LR0Parser(LRParser):
    def build_automaton(self):
        if self.automaton_built:
            # TODO: Warn user
            return
        init = LRAutomatonState(self.closure(LRItem(self.grammar.prods[0], 0)))
        self.build_automaton_from_init(init)

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
        p = LR1Parser(sys.argv[1])
    else:
        #lr0 = LR0Parser()
        p = LR1Parser()
    
    ret = p.closure(
        LRItem(
            p.grammar.prods[0],
            0,
            # ['$']
        )
    )
    pprint(ret)
    """
    for state in p.automaton_states:
        print(state.__repr__())
        print(64 *'-')
    """
    print(p.automaton_states[0] == p.automaton_states[-1])
    for i, state in enumerate(p.automaton_states):
        print('State {} = {}\n'.format(i, state) + 64*'-')
    pprint(p.automaton_transitions)
    p.visualize_automaton()
