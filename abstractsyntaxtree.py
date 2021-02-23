from grammar import Production, EPSILON
from pprint import pformat
class AbstractSyntaxTree(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.root = None
            self.desc = []
            self.prod_id = None
            self.node_id = None
        if len(args) == 1:
            if isinstance(args[0], Production):
                self.root = args[0].lhs
                desc = []
                for symbol in args[0].rhs:
                    desc.append(AbstractSyntaxTree(symbol))
                self.desc = desc
                self.prod_id = None
            elif isinstance(args[0], str):
                self.root = args[0]
                self.desc = []
                self.prod_id = None

    def __str__(self):
        return '{}->{}'.format(self.root, pformat(self.desc))

    def __repr__(self):
        return str(self)
