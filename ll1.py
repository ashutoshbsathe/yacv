from grammar import Grammar, first, EPSILON
import pandas as pd
from pprint import pprint

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
        stack = ['S\'']
        while stack[-1] != '$':
            top = stack[-1] 
            a = string[0]
            if top == a:
                stack.pop(-1)
                a = string.pop(0)
            elif top in self.grammar.terminals:
                raise ValueError('Error because top = {}, terminal'.format(top))
            elif self.parsing_table.at[top, a] == ERROR:
                raise ValueError('Error because parsing table errored out')
            elif self.parsing_table.at[top, a] != ACCEPT:
                prod = self.parsing_table.at[top, a][0]
                print(prod)
                stack.pop(-1)
                if prod.rhs[0] != EPSILON:
                    stack += list(reversed(prod.rhs))




if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ll1 = LL1Parser(sys.argv[1])
    else:
        ll1 = LL1Parser()
    ll1.parse(['id', '+', 'id', '*', 'id'])
