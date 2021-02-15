from grammar import Grammar, first, EPSILON
from pprint import pprint
from copy import deepcopy
from collections import OrderedDict
import pandas as pd

ACTION = 'ACTION'
ACCEPT = 'ACC'
ERROR  = ''
GOTO   = 'GOTO'

class LR1Item(object):
    def __init__(self, production=None, dot_pos=0, lookaheads=[]):
        # A -> . a A, dot_pos = 0
        # A -> a . A, dot_pos = 1
        # A -> a A ., dot_pos = 2
        self.production = production
        self.dot_pos = dot_pos
        self.lookaheads = lookaheads
        self.update_reduce()

    def update_reduce(self):
        if self.dot_pos == len(self.production.rhs) \
            or self.production.rhs[self.dot_pos] == '$' \
            or self.production.rhs[self.dot_pos] == EPSILON:
            self.reduce = True
        else:
            self.reduce = False
    def __str__(self):
        lhs, rhs = self.production.lhs, self.production.rhs
        dot_pos = self.dot_pos
        return '{} -> {}•{}, {}'.format(
                    lhs,
                    ''.join(rhs[:dot_pos]) if dot_pos > 0 else '',
                    ''.join(rhs[dot_pos:]),
                    self.lookaheads
                )

    def __repr__(self):
        return '< ' + str(self) + ' > at {}'.format(hex(id(self)))

class LR1Parser(object):
    def __init__(self, fname='ll1-expression-grammar.txt'):
        self.grammar = Grammar(fname)
        self.automaton_states = []
        self.automaton_transitions = OrderedDict()
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
        # self.build_parsing_table()
    
    def closure(self, i):
        # i is an LR0Item
        ret = []
        queue = i if isinstance(i, list) else [i]
        # counter = 10
        visited_symbols = set()
        while queue:
            item = queue.pop(0)
            ret.append(item)
            if item.reduce:
                continue
            next_symbol = item.production.rhs[item.dot_pos]
            if next_symbol != EPSILON \
            and not next_symbol in self.grammar.terminals:
                # print('next_symbol = {}'.format(next_symbol))
                if next_symbol in visited_symbols:
                    continue
                else:
                    visited_symbols.add(next_symbol)
                prodnos = self.grammar.nonterminals[next_symbol]['prods_lhs']
                print('next_symbol = {}, FIRST({}) = {}'.format(
                        next_symbol,
                        item.production.rhs[item.dot_pos+1:]+['$'],
                        first(
                            self.grammar,
                            item.production.rhs[item.dot_pos:]+item.lookaheads
                        )
                    ))
                lookaheads = sorted(list(
                    first(self.grammar, 
                          item.production.rhs[item.dot_pos:]+item.lookaheads)
                    .difference(set([EPSILON]))
                ))
                for prodno in prodnos:
                    # print('Attempting to add new production {}'.format(self.grammar.prods[prodno]))
                    new_item = LR1Item(
                            self.grammar.prods[prodno],
                            dot_pos = 0,
                            lookaheads = lookaheads
                        )
                    if new_item not in ret:
                        queue.append(new_item)
            # counter -= 1
            # if counter < 0:
            #     break

        return ret
    
    def is_reduce_state(self, state):
        if isinstance(state, tuple):
            state = list(state)
        elif not isinstance(state, list):
            raise ValueError('type(state) must be tuple or list, received {}'.format(type(state)))
        for item in state:
            if item.reduce:
                return True
        return False

    def is_accept_state(self, state):
        if isinstance(state, tuple):
            state = list(state)
        elif not isinstance(state, list):
            raise ValueError('type(state) must be tuple or list, received {}'.format(type(state)))
        for item in state:
            if item.reduce and self.grammar.prods.index(item.production) == 0:
                return True
        return False

    def stringify_state(self, state):
        if isinstance(state, tuple):
            state = list(state)
        elif not isinstance(state, list):
            raise ValueError('type(state) must be tuple or list, received {}'.format(type(state)))
        return '\n'.join([str(x) for x in state])

    def build_automaton(self):
        # TODO: This function is incredibly messy
        # Think about cleaning it into a separate class
        state = self.closure(LR1Item(
            self.grammar.prods[0], dot_pos=0, lookaheads=['$']
        ))
        queue = [(state, 0)]
        unique_states = set()
        num_states = 0
        while queue:
            state, state_id = queue.pop(0)
            state_string = self.stringify_state(state)
            """
            if state_string not in unique_states:
                unique_states.add(state_string)
            else:
                continue
            """
            for item in state:
                item.lookaheads = sorted(item.lookaheads)
            if state_string not in unique_states:
                self.automaton_states.append(tuple(deepcopy(state)))
                self.automaton_transitions['s' + str(state_id)] = {}
            next_symbols = {}
            print('state = {}'.format(state_string))
            for item in state:
                if item.reduce:
                    continue
                key = item.production.rhs[item.dot_pos]
                if key not in next_symbols.keys():
                    next_symbols[key] = []
                item.dot_pos += 1
                item.update_reduce()
                next_symbols[key].append(item)
            pprint(next_symbols)
            for symbol, items in next_symbols.items():
                print('On symbol {}, items = {}'.format(symbol, items))
                new_state = self.closure(items)
                new_state_string = self.stringify_state(new_state)
                print('GOTO(state, {}) = {}'.format(symbol, new_state_string))
                if not new_state_string in unique_states:
                    unique_states.add(new_state_string)
                    num_states += 1
                    queue.append((new_state, num_states))
                    self.automaton_transitions['s' + str(state_id)][symbol] = \
                            's' + str(num_states)
                    self.automaton_states.append(tuple(deepcopy(new_state)))
                    self.automaton_transitions['s' + str(num_states)] = {}
                else:
                    # TODO: Find a better way for this
                    pprint(unique_states)
                    print('Matching state ="{}"'.format(new_state_string))
                    for i, x in enumerate(self.automaton_states):
                        print('Is it {} ?'.format(self.stringify_state(x)))
                        if self.stringify_state(x) == new_state_string:
                            print('Found match')
                            new_state_id = i
                    pprint(queue)
                    self.automaton_transitions['s' + str(state_id)][symbol] = \
                            's' + str(new_state_id)

            print(64 *'-')
        pprint(self.automaton_states)
        pprint(self.automaton_transitions)
    
    def build_parsing_table(self):
        pprint(self.parsing_table)
        print(self.grammar.prods)
        terminals = self.grammar.terminals
        for state_id, transitions in self.automaton_transitions.items():
            state = self.automaton_states[int(state_id[1:])]
            if self.is_accept_state(state):
                col = (ACTION, '$')
                self.parsing_table.at[state_id, col] = ACCEPT
            elif self.is_reduce_state(state):
                for symbol in self.grammar.terminals:
                    col = (ACTION, symbol)
                    if self.parsing_table.at[state_id, col] == ERROR:
                        self.parsing_table.at[state_id, col] = []
                    for item in state:
                        if item.reduce:
                            prod_id = self.grammar.prods.index(item.production)
                            entry = 'r' + str(prod_id)
                            self.parsing_table.at[state_id, col].append(entry)
            for symbol, new_state in transitions.items():
                if symbol in terminals:
                    entry = new_state
                    col = (ACTION, symbol)
                else:
                    entry = new_state[1:]
                    col = (GOTO, symbol)
                if self.parsing_table.at[state_id, col] == ERROR:
                    self.parsing_table.at[state_id, col] = []
                self.parsing_table.at[state_id, col].append(entry)

        pprint(self.parsing_table)
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        #lr0 = LR0Parser(sys.argv[1])
        slr1 = LR1Parser(sys.argv[1])
    else:
        #lr0 = LR0Parser()
        slr1 = LR1Parser()
