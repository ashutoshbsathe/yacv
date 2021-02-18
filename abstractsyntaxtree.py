from grammar import Production, EPSILON

class AbstractSyntaxTree(object):
    def __init__(self, *args):
        if len(args) == 0:
            self.root = None
            self.desc = []
        if len(args) == 1:
            if isinstance(args[0], Production):
                self.root = args[0].lhs
                desc = []
                for symbol in args[0].rhs:
                    desc.append(ParseTree(symbol))
                self.desc = desc
            elif isinstance(args[0], str):
                self.root = args[0]
                self.desc = []

    def __str__(self):
        return '[root = {}, desc = {}]'.format(self.root, self.desc)

    def __repr__(self):
        return 'ParseTree object ' + str(self) + ' at {}'.format(hex(id(self)))
