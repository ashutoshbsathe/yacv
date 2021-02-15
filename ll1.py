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
        pprint(self.parsing_table)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        ll1 = LL1Parser(sys.argv[1])
    else:
        ll1 = LL1Parser()
