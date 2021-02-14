from collections import OrderedDict
from pprint import pprint
EPSILON = ''
class Production(object):
    def __init__(self, lhs=None, rhs=[]):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        rhs = 'ϵ' if self.rhs[0] == EPSILON else ''.join(self.rhs)
        return '{} -> {}'.format(self.lhs, rhs)
    
    def __repr__(self):
        return str(self)

class LRParserItem(object):
    def __init__(self, production=None, dot_pos=0, lookaheads=[], lr1=True):
        self.production = production
        self.dot_pos = dot_pos
        self.lookaheads = lookaheads
        self.lr1 = lr1
    
    def __str__(self):
        item = '{} -> {}•{}'.format(
                    self.production.lhs,
                    self.production.rhs[:self.dot_pos],
                    self.production.rhs[self.dot_pos:],
                )
        if self.lr1:
            return item + ', {}'.format(self.lookaheads)
        else:
            return item

    def __repr__(self):
        return str(self)

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
        x = first(g, rhs)
        ret = ret.union(x)
        i = 0
        while EPSILON in x:
            # note that, if all the symbols are nullable
            # then i will exceed list length
            # this is handled in the base case of recursion
            x = first(g, rhs[i+1:])
            i += 1
            ret = ret.union(x)
    return ret

class Grammar(object):
    def __init__(self, fname='simple-grammar.txt'):
        lines = [x.strip() for x in open(fname).readlines()] 
        self.prods = [] # list containing all the productions
        for line in lines:
            # TODO: Find out erroneous grammars if the following generate a `ValuError`
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
        # Update nonterminals_on_rhs for every prod using above data
        for prodno, prod in enumerate(self.prods):
            lhs, rhs = prod.lhs, prod.rhs
            print(lhs, rhs)
            for i, symbol in enumerate(rhs):
                if symbol in self.nonterminals.keys():
                    self.nonterminals[symbol]['prods_rhs'].append((prodno, i))
            if rhs[0] not in self.nonterminals.keys():
                self.nonterminals[lhs]['first'].add(rhs[0])
                if rhs[0] == EPSILON:
                    self.nonterminals[lhs]['nullable'] = True
        self.nonterminals[self.prods[0].lhs]['follow'].add('$')
        # Calculate FIRST set for every non terminal
        self.build_first()
        # Calculate FOLLOW set for every non terminal
        self.build_follow()

    def build_first(self):
        nonempty_firsts = []
        for symbol, info in self.nonterminals.items():
            if info['first']:
                nonempty_firsts.append(symbol)
        while nonempty_firsts:
            symbol = nonempty_firsts.pop(0)
            # If this symbol appears in front of some prod, add that
            for prodno, idx in self.nonterminals[symbol]['prods_rhs']:
                if idx == 0 and self.prods[prodno].lhs != symbol:
                    new_symbol = self.prods[prodno].lhs
                    print('Found production {} where FIRST({}) = FIRST({})'.format(
                        self.prods[prodno], self.prods[prodno].lhs, symbol
                    ))
                    # make union of 2 first sets
                    tmp = self.nonterminals[new_symbol]['first'].union(
                        self.nonterminals[symbol]['first']
                    )
                    self.nonterminals[new_symbol]['first'] = tmp
                    nonempty_firsts.append(new_symbol)

    def build_follow(self):
        pass

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        g = Grammar()
    else:
        g = Grammar(sys.argv[1])
    pprint(g.prods)
    pprint(g.nonterminals)
    for nt in g.nonterminals.keys():
        print('FIRST({}) = {}'.format(nt, first(g, [nt])))
