from collections import OrderedDict
from pprint import pprint
from constants import *
class Production(object):
    def __init__(self, lhs=None, rhs=[]):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        rhs = 'ϵ' if self.rhs[0] == EPSILON else ''.join(self.rhs)
        return '{} -> {}'.format(self.lhs, rhs)
    
    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        if not isinstance(other, Production):
            return False
        return self.lhs == other.lhs and self.rhs == other.rhs
    
    def __ne__(self, other):
        return not self == other
def first(g, s):
    # g: Grammar object
    # s: RHS or Part of RHS as list
    if not s:
        return set() # empty set
    if s[0] == EPSILON:
        return set([EPSILON]) # set with epsilon in it
    if s[0] not in g.nonterminals.keys():
        return set([s[0]])
    # At this point, s[0] must be a non terminal
    ret = set()
    for prodno in g.nonterminals[s[0]]['prods_lhs']:
        rhs = g.prods[prodno].rhs
        if rhs[0] == s[0]:
            # left recursion
            continue
        x = first(g, rhs)
        ret = ret.union(x)
        """
        i = 0
        while EPSILON in x:
            # note that, if all the symbols are nullable
            # then i will exceed list length
            # this is handled in the base case of recursion
            x = first(g, rhs[i+1:])
            i += 1
            ret = ret.union(x)
        """
    if EPSILON in ret:
        x = first(g, s[1:])
        ret = ret.union(x)
    return ret

class Grammar(object):
    def __init__(self, fname='simple-grammar.txt'):
        lines = [x.strip() for x in open(fname).readlines()] 
        self.prods = [] # list containing all the productions
        all_symbols = set()
        for line in lines:
            # TODO: If ValueError is generated when splitting
            # report unrecognized grammar
            if line == '':
                continue
            lhs, rhs = line.split('->')
            lhs = lhs.strip()
            rhs = [x for x in rhs.split(' ') if x]
            # TODO: find a better way to do this
            for i, _ in enumerate(rhs):
                if rhs[i] == "\'\'":
                    rhs[i] = EPSILON
            self.prods.append(
                Production(lhs, rhs)
            )
            all_symbols = all_symbols.union(rhs)
        # Augment the grammar
        self.prods.insert(0, Production('S\'', [self.prods[0].lhs, '$']))
        # Accumulate nonterminal information
        self.nonterminals = OrderedDict()
        for i, prod in enumerate(self.prods):
            lhs, rhs = prod.lhs, prod.rhs
            if lhs not in self.nonterminals.keys():
                self.nonterminals[lhs] = {
                    # number of productions this nonterminal is on the LHS of
                    'prods_lhs' : [i],
                    # where does this non terminal appear on RHS ? 
                    # what prod and what place ?
                    'prods_rhs' : [],
                    'first'     : set(),
                    'follow'    : set(),
                    'nullable'  : False
                }
            else:
                self.nonterminals[lhs]['prods_lhs'].append(i)
        self.terminals = all_symbols.difference(set(self.nonterminals.keys()))
        if EPSILON in self.terminals:
            self.terminals = self.terminals.difference(set([EPSILON]))
        self.terminals.add('$')
        self.terminals = sorted(self.terminals)
        # Update nonterminals_on_rhs for every prod using above data
        for prodno, prod in enumerate(self.prods):
            lhs, rhs = prod.lhs, prod.rhs
            for i, symbol in enumerate(rhs):
                if symbol in self.nonterminals.keys():
                    self.nonterminals[symbol]['prods_rhs'].append((prodno, i))
        self.build_first()
        self.build_follow()

    def build_first(self):
        # inefficient method, but should work fine for most small grammars
        for nt in self.nonterminals.keys():
            tmp = first(self, [nt])
            if EPSILON in tmp:
                self.nonterminals[nt]['nullable'] = True
            self.nonterminals[nt]['first'] = tmp

    def build_follow(self):
        self.nonterminals[self.prods[0].lhs]['follow'].add('$')
        for nt in self.nonterminals.keys():
            # Where does this symbol occur on RHS ?
            s = set()
            for prodno, idx in self.nonterminals[nt]['prods_rhs']:
                print('Needed FIRST({}) = {} for FOLLOW({})'.format(
                    self.prods[prodno].rhs[idx+1:], 
                    first(self, self.prods[prodno].rhs[idx+1:]), 
                    nt
                ))
                f = first(self, self.prods[prodno].rhs[idx+1:])
                if not f or EPSILON in f:
                    f.add('$')
                s = s.union(f)
                s = s.difference(set([EPSILON]))
            self.nonterminals[nt]['follow'] = s
            print('FOLLOW({}) = {}'.format(nt, s))
        for prod in self.prods:
            print('At production {}'.format(prod))
            # Is there a production A -> BC such that C is NULLABLE ?
            lhs, rhs = prod.lhs, prod.rhs
            reversed_rhs = rhs[::-1]
            for i, symbol in enumerate(reversed_rhs):
                print('i = {}, symbol = {}'.format(i, symbol))
                if symbol not in self.nonterminals.keys():
                    break
                if self.nonterminals[symbol]['nullable'] and (i+1) < len(rhs):
                    if reversed_rhs[i+1] in self.terminals:
                        continue
                    s1 = self.nonterminals[reversed_rhs[i+1]]['follow']
                    s2 = self.nonterminals[lhs]['follow']
                    s1 = s1.union(s2)
                    self.nonterminals[reversed_rhs[i+1]]['follow'] = s1
                    if i == 0:
                        s3 = self.nonterminals[symbol]['follow']
                        s3 = s3.union(s2)
                        self.nonterminals[symbol]['follow'] = s3
                        print('Production {} has nullable symbol {} at the end, updated FOLLOW({}) = {}'.format(prod, symbol, symbol, s3))
                    print('Production {} has nullable symbol {}, changed FOLLOW({}) to {}'.format(prod, symbol, reversed_rhs[i+1], s1))
            if rhs[-1] in self.nonterminals.keys():
                self.nonterminals[rhs[-1]]['follow'] = \
                        self.nonterminals[rhs[-1]]['follow'].union(
                            self.nonterminals[lhs]['follow']
                        )
            print(64*'-')



if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        g = Grammar()
    else:
        g = Grammar(sys.argv[1])
    pprint(g.prods)
    print(64*'-')
    for nt in g.nonterminals.keys():
        print('FIRST({}) = {}'.format(nt, g.nonterminals[nt]['first']))
    print(64*'-')
    for nt in g.nonterminals.keys():
        print('FOLLOW({}) = {}'.format(nt, g.nonterminals[nt]['follow']))
