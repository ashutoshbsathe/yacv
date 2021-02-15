from grammar import Grammar, first, EPSILON
from pprint import pprint
from copy import deepcopy

class LR0Item(object):
    def __init__(self, production=None, dot_pos=0):
        # A -> . a A, dot_pos = 0
        # A -> a . A, dot_pos = 1
        # A -> a A ., dot_pos = 2
        self.production = production
        self.dot_pos = dot_pos
        self.update_reduce()

    def update_reduce(self):
        if self.dot_pos == len(self.production.rhs) \
            or self.production.rhs[self.dot_pos] == '$':
            self.reduce = True
        else:
            self.reduce = False
    def __str__(self):
        lhs, rhs = self.production.lhs, self.production.rhs
        dot_pos = self.dot_pos
        return '{} -> {}•{}'.format(
                    lhs,
                    ''.join(rhs[:dot_pos]) if dot_pos > 0 else '',
                    ''.join(rhs[dot_pos:])
                )

    def __repr__(self):
        return str(self)

class LR0Parser(object):
    def __init__(self, fname='ll1-expression-grammar.txt'):
        self.grammar = Grammar(fname)
        self.automaton_states = []
        self.automaton_transitions = {}
        self.build_automaton()
    
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
                for prodno in prodnos:
                    # print('Attempting to add new production {}'.format(self.grammar.prods[prodno]))
                    new_item = LR0Item(
                            self.grammar.prods[prodno],
                            dot_pos = 0
                        )
                    if new_item not in ret:
                        queue.append(new_item)
            # counter -= 1
            # if counter < 0:
            #     break

        return ret
    
    def is_reduce_state(self, state):
        if isinstance(state, tuple):
            state = list(*state)
        elif not isinstance(state, list):
            raise ValueError('type(state) must be tuple or list, received {}'.format(type(state)))
        for item in state:
            if item.reduce:
                return True
        return False

    def stringify_state(self, state):
        if isinstance(state, tuple):
            state = list(*state)
        elif not isinstance(state, list):
            raise ValueError('type(state) must be tuple or list, received {}'.format(type(state)))
        return '\n'.join([str(x) for x in state])

    def build_automaton(self):
        # TODO: This function is incredibly messy
        # Think about cleaning it into a separate class
        state = self.closure(LR0Item(self.grammar.prods[0], dot_pos=0))
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

            print(64 *'-')
            # counter -= 1
            # if counter < 0:
            #    break
        pprint(self.automaton_states)
        pprint(self.automaton_transitions)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        lr0 = LR0Parser(sys.argv[1])
    else:
        lr0 = LR0Parser()
