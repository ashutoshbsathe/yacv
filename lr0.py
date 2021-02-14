from grammar import Grammar, first, EPSILON
from pprint import pprint

class LR0Item(object):
    def __init__(self, production=None, dot_pos=0):
        # A -> . a A, dot_pos = 0
        # A -> a . A, dot_pos = 1
        # A -> a A ., dot_pos = 2
        self.production = production
        self.dot_pos = dot_pos
        self.update_reduce()

    def update_reduce(self):
        if self.dot_pos == len(self.production.rhs):
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
        self.automaton_transitions = []
        self.build_automaton()
    
    def closure(self, i):
        # i is an LR0Item
        print(i, i.dot_pos)
        ret = []
        queue = [i]
        # counter = 10
        visited_symbols = set()
        while queue:
            item = queue.pop(0)
            ret.append(item)
            next_symbol = item.production.rhs[item.dot_pos]
            if not next_symbol in self.grammar.terminals:
                print('next_symbol = {}'.format(next_symbol))
                if next_symbol in visited_symbols:
                    continue
                else:
                    visited_symbols.add(next_symbol)
                prodnos = self.grammar.nonterminals[next_symbol]['prods_lhs']
                for prodno in prodnos:
                    print('Attempting to add new production {}'.format(self.grammar.prods[prodno]))
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
    def build_automaton(self):
        state = self.closure(LR0Item(self.grammar.prods[0], dot_pos=0))
        queue = [state]
        counter = 1
        unique_states = set()
        while queue:
            state = queue.pop(0)
            state_string = '$$'.join([str(x) for x in state])
            if state_string not in unique_states:
                unique_states.add(state_string)
            else:
                continue
            self.automaton_states.append(tuple(state))
            for item in state:
                item.dot_pos += 1
                item.update_reduce()
                if not item.reduce:
                    new_state = self.closure(item)
                    print(new_state)
                    queue.append(new_state)
            # counter -= 1
            # if counter < 0:
            #    break
        for x in self.automaton_states:
            print(x)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        lr0 = LR0Parser(sys.argv[1])
    else:
        lr0 = LR0Parser()
