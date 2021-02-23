import pygraphviz as pgv
from manimlib import *
import numpy as np
import sys
sys.path.append('/home/ashutosh/parser-vis')
from grammar import EPSILON
from ll1 import *
from lr import *
from abstractsyntaxtree import AbstractSyntaxTree
COLORS = [
    '#FF7F50', # 'coral',
    '#8B008B', # 'darkmagenta',
    '#006400', # 'darkblue',
    '#8B0000', # 'darkred',
    '#FF1493', # 'deeppink',
    '#1E90FF', # 'dodgerblue',
    '#8A2BE2', # 'blueviolet',
    '#008B8B', # 'darkcyan',
    '#FFFF00', # 'yellow',
    '#191970', # 'mediumslateblue',
    '#A52A2A', # 'brown',
    '#FFA500', # 'orange',
    '#008080', # 'teal',
    '#2E8B57', # 'seagreen',
    '#00FF7F', # 'springgreen',
    '#FF6347', # 'tomato'
]
INFINITY = 2048
GRAMMAR = 'expression-grammar.txt'
<<<<<<< HEAD
STRING = 'id + id * id / id - id + ( id / id / id )'
=======
STRING = 'id + id * id / id - ( id + id )'
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
class GraphvizGraph(VGroup):
    def __init__(self, graph, **kwargs):
        digest_config(self, kwargs, locals())
        super().__init__(**kwargs)
        self.new_bbox = None
        self.scale_x = None
        self.scale_y = None
        self.graph = graph
        x, y, l, w = self.graph.graph_attr['bb'].split(',')
        self.bounding_box = [float(x), float(y), float(l), float(w)]
        self.nodes = {}
        self.edges = {}
        self.graph_added = False
        self.add_graph()

    def gridify(self, x, y):
        assert self.bounding_box is not None and len(self.bounding_box) == 4
        bounding_box = self.bounding_box
        if self.new_bbox is None:
            width = bounding_box[2] - bounding_box[0]
            height = bounding_box[3] - bounding_box[1]
            ratio = width / height
            # Find the maximum bbox so that it fits "nicely"
            old_bbox = (0, 0)
            for new_height in np.linspace(1.0, 7.0, num=100):
                new_width = ratio * new_height
                if new_width <= 10:
                    old_bbox = (new_width, new_height)
            ref_width, ref_height = old_bbox
            new_bbox = [-ref_width/2, -ref_height/2, ref_width/2, ref_height/2]
            scale_x = ref_width / width
            scale_y = ref_height / height
            self.new_bbox = new_bbox
            self.scale_x = scale_x
            self.scale_y = scale_y
        assert self.scale_x is not None and self.scale_y is not None
        new_x = self.new_bbox[0] + self.scale_x * float(x)
        new_y = self.new_bbox[1] + self.scale_y * float(y)
        return new_x, new_y
    
    # https://codereview.stackexchange.com/questions/240710/pure-python-b%C3%A9zier-curve-implementation
    def bezier_curve(self, control_points, n=11):
        return [
            self.bezier_point(control_points, t)
            for t in (
                i * 1. / (n - 1) for i in range(n)
            )
        ]

    def bezier_point(self, control_points, t):
        if len(control_points) == 1:
            result,  = control_points
            return result
        control_linestring = zip(control_points[:-1], control_points[1:])
        return self.bezier_point([
            (1 - t) * p1 + t * p2 for p1, p2 in control_linestring
        ], t)
    
    def coord(self, x, y, z=0):
        return np.array([x, y, z])

    def add_graph(self):
        if self.graph_added:
            # TODO: warn the user maybe ?
            return 
        g = self.graph
        for e in g.edges():
            if e.attr['style'] == 'invis':
                continue
            print(e.attr['pos'])
            points = [np.asarray(self.gridify(*x.split(',')[-2:])) \
                    for x in e.attr['pos'].split(' ')]
            # we're "beziering" the gridified points
            # TODO: will it be more accurate if we used raw coords ?
            bezier_pts = self.bezier_curve(points, n=101)
            bezier_pts = [self.coord(*x) for x in bezier_pts]
            path = VMobject()
            path.set_points_smoothly(bezier_pts)
            path.set_color(e.attr['color'])
            self.add(path)
            key = '(' + str(e[0]) + ',' + str(e[1]) + ')'
            self.edges[key] = path
        for n in g.nodes():
            label = n.attr['label'].replace('&#x3B5;', '\epsilon')
            print(label)
            dot = Tex('{{' + label + '}}')
            x, y = n.attr['pos'].split(',')
            x, y = self.gridify(x, y)
            dot.move_to(x*RIGHT + y*UP)
            dot.scale(0.5)
            if n.attr['fontcolor']:
                dot.set_color(n.attr['fontcolor'])
            self.add(dot)
            self.nodes[str(n)] = dot
        self.graph_added = True

def transform_graphviz_graphs(old, new):
    common_nodes = set(old.nodes.keys()).intersection(set(new.nodes.keys()))
    common_edges = set(old.edges.keys()).intersection(set(new.edges.keys()))
    
    anims = []
<<<<<<< HEAD
    
    def is_equiv_vertices(n):
        return int(n) < 0 or old.graph.get_node(n).attr['label'][0] == \
                new.graph.get_node(n).attr['label'][0]
    for n in list(common_nodes):
        if is_equiv_vertices(n):
            anims.append(Transform(old.nodes[n], new.nodes[n]))
        else:
            anims.append(FadeOut(old.nodes[n]))
            anims.append(FadeIn(new.nodes[n]))

    for e in list(common_edges):
        v0, v1 = e[1:-1].split(',')
        if is_equiv_vertices(v0) and is_equiv_vertices(v1):
            anims.append(Transform(old.edges[e], new.edges[e]))
        else:
            anims.append(FadeOut(old.edges[e]))
            anims.append(FadeIn(new.edges[e]))
=======
    for n in list(common_nodes):
        anims.append(Transform(old.nodes[n], new.nodes[n]))

    for e in list(common_edges):
        anims.append(Transform(old.edges[e], new.edges[e]))
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f

    old_nodes = set(old.nodes.keys()).difference(common_nodes)
    old_edges = set(old.edges.keys()).difference(common_edges)
    for n in list(old_nodes):
        anims.append(FadeOut(old.nodes[n]))

    for e in list(old_edges):
        anims.append(FadeOut(old.edges[e]))

    new_nodes = set(new.nodes.keys()).difference(common_nodes)
    new_edges = set(new.edges.keys()).difference(common_edges)
    for n in list(new_nodes):
<<<<<<< HEAD
        anims.append(FadeIn(new.nodes[n]))

    for e in list(new_edges):
        anims.append(FadeIn(new.edges[e]))

    return anims

def ast_to_graphviz_inbuilt_nodeid(ast, g):
    G = pgv.AGraph(name='AST{}'.format(ast.node_id), directed=True)
    stack = [ast]
    prods = []
    while stack:
        top = stack.pop(0)
        node = top.node_id 
        assert node is not None 
        if str(node) not in G.nodes():
            G.add_node(node, label=top.root)
            # node_id += 1
        if top.prod_id is not None:
            color = COLORS[top.prod_id % len(COLORS)]
            G.get_node(node).attr['fontcolor'] = color
        desc_ids = []
        for desc in top.desc:
            if desc.root == EPSILON:
                label = G.get_node(node).attr['label']
                label = '<' + label + ' = &#x3B5;>'
                G.get_node(node).attr['label'] = label
                break
            assert desc.node_id is not None
            G.add_node(desc.node_id, label=desc.root)
            if top.prod_id is not None:
                color = COLORS[top.prod_id % len(COLORS)]
            else:
                color = '#FFFF00'
            G.add_edge(node, desc.node_id, color=color)
            desc_ids.append(desc.node_id)
            stack.append(desc)
            # node_id += 1
        prods.append(desc_ids)

    # Figure out terminal nodes
    terminal_nodes = []
    stack = [G.nodes()[0]]
    visited = []
    terminals = g.terminals
    while stack:
        node = stack.pop(-1)
        if node not in visited:
            visited.append(node)
            if node.attr['label'] in terminals:
                terminal_nodes.append(node)
            for i in range(len(G.successors(node))-1, -1, -1):
                stack.append(G.successors(node)[i])
    
    # Fix the alignment of RHS of productions
    for i, prod in enumerate(prods):
        nonterminals = []
        for node_id in prod:
            if G.get_node(node_id).attr['label'] in terminals:
                continue
            nonterminals.append(G.get_node(node_id))
        if len(nonterminals) <= 1:
            continue
        nt = G.subgraph(nonterminals, name='Production{}AST{}'.format(i, ast.node_id))
        nt.graph_attr['rank'] = 'same'
        for j in range(len(nt.nodes())-1):
            nt.add_edge(nonterminals[j], nonterminals[j+1], style='dashed', color='#000000',\
                    weight=INFINITY)
    """
    # Finally, add the terminal subgraphs
    t = G.add_subgraph(terminal_nodes, name='Terminals{}'.format(init_node))
    t.graph_attr['rank'] = 'max'
    for i in range(len(t.nodes())-1):
        t.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis')
    """

    return G, terminal_nodes
=======
        anims.append(ShowCreation(new.nodes[n]))

    for e in list(new_edges):
        anims.append(ShowCreation(new.edges[e]))

    return anims

>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
def ast_to_graphviz(ast, g, init_node=0):
    node_id = init_node
    G = pgv.AGraph(name='AbstractSyntaxTree{}'.format(init_node), directed=True)
    stack = [(ast, node_id)]
    prods = []
    while stack:
        top, node = stack.pop(0)
        if str(node) not in G.nodes():
            G.add_node(node_id, label=top.root)
            node_id += 1
        if top.prod_id is not None:
            color = COLORS[top.prod_id % len(COLORS)]
            G.get_node(node).attr['fontcolor'] = color
        desc_ids = []
        for desc in top.desc:
            if desc.root == EPSILON:
                label = G.get_node(node).attr['label']
                label = '<' + label + ' = &#x3B5;>'
                G.get_node(node).attr['label'] = label
                break
            G.add_node(node_id, label=desc.root)
            if top.prod_id is not None:
                color = COLORS[top.prod_id % len(COLORS)]
            else:
                color = '#FFFF00'
            G.add_edge(node, node_id, color=color)
            desc_ids.append(node_id)
            stack.append((desc, node_id))
            node_id += 1
        prods.append(desc_ids)

    # Figure out terminal nodes
    terminal_nodes = []
    stack = [G.nodes()[0]]
    visited = []
    terminals = g.terminals
    while stack:
        node = stack.pop(-1)
        if node not in visited:
            visited.append(node)
            if node.attr['label'] in terminals:
                terminal_nodes.append(node)
            for i in range(len(G.successors(node))-1, -1, -1):
                stack.append(G.successors(node)[i])
    
    # Fix the alignment of RHS of productions
    for i, prod in enumerate(prods):
        nonterminals = []
        for node_id in prod:
            if G.get_node(node_id).attr['label'] in terminals:
                continue
            nonterminals.append(G.get_node(node_id))
        if len(nonterminals) <= 1:
            continue
        nt = G.subgraph(nonterminals, name='Production{}AST{}'.format(i, init_node))
        nt.graph_attr['rank'] = 'same'
        for j in range(len(nt.nodes())-1):
            nt.add_edge(nonterminals[j], nonterminals[j+1], style='dashed', color='#000000',\
                    weight=INFINITY)
    """
    # Finally, add the terminal subgraphs
    t = G.add_subgraph(terminal_nodes, name='Terminals{}'.format(init_node))
    t.graph_attr['rank'] = 'max'
    for i in range(len(t.nodes())-1):
        t.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis')
    """

    return G, terminal_nodes

def lr_stack_to_graphviz(stack, grammar):
    prod_subgraphs = []
    terminal_nodes = []
    root_nodes = []
    node_id = 0
    ret = pgv.AGraph(directed=True)
    for item in stack:
        if not isinstance(item, AbstractSyntaxTree):
            continue
<<<<<<< HEAD
        if len(item.desc) > 1:
            root_nodes.append(item.node_id)
        # g, t_nodes = ast_to_graphviz(item, grammar, node_id)
        g, t_nodes = ast_to_graphviz_inbuilt_nodeid(item, grammar)
=======
        root_nodes.append(node_id)
        g, t_nodes = ast_to_graphviz(item, grammar, node_id)
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
        node_id += len(g.nodes())
        terminal_nodes.extend(t_nodes)
        # Add all the nodes and edges from `g` to `ret`
        for n in g.nodes():
            ret.add_node(n)
            for k in n.attr.keys():
                ret.get_node(n).attr[k] = n.attr[k]
        for e in g.edges():
            ret.add_edge(e)
            for k in e.attr.keys():
                print(k, e.attr[k])
                ret.get_edge(e[0], e[1]).attr[k] = e.attr[k]
        for graph in g.subgraphs():
            prod = ret.add_subgraph(graph.nodes(), name=graph.name)
            prod.graph_attr['rank'] = 'same'
            # I assume we don't need to add extra edges here
            # because I believe the subgraph edges too, are already added
            # OR maybe we just add subgraph first and then the remaining
            # graph ?
            for e in graph.edges():
                prod.add_edge(e[0], e[1], style='invis', weight=INFINITY)

<<<<<<< HEAD
    if len(root_nodes) > 1:
        # Add an auxilliary root node 
        ret.add_node(-1, style='invis', label='')
        for n in root_nodes:
            ret.add_edge(-1, n, style='invis')
        roots = ret.add_subgraph(root_nodes, name='Roots')
        roots.graph_attr['rank'] = 'min'
        for i in range(len(roots.nodes())-1):
            roots.add_edge(root_nodes[i], root_nodes[i+1], style='invis', weight=INFINITY)
=======
    # Also make a subgraph of roots so that their order is preserved
    for i in range(len(root_nodes)):
        for j in range(len(root_nodes)):
            ret.add_edge(root_nodes[i], root_nodes[j], style='invis')
        
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
    # Finally, all the things are done
    # now let's add the terminals
    term = ret.add_subgraph(terminal_nodes, name='Terminals')
    term.graph_attr['rank'] = 'sink'
    for i in range(len(term.nodes()) - 1):
<<<<<<< HEAD
        term.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis', weight=INFINITY)
=======
        term.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis')
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
   
    ret.edge_attr['dir'] = 'none'
    ret.node_attr['ordering'] = 'out'
    ret.node_attr['shape'] = 'none'
    ret.node_attr['height'] = 0
    ret.node_attr['width'] = 0
    ret.node_attr['margin'] = 0.1
    print(ret.string())
    ret.layout('dot')
    ret.draw('output.png')
    print('Returning G')
    return ret


class AnimateGraphs(Scene):
    def construct(self):
<<<<<<< HEAD
        """
        g = LR1Parser(GRAMMAR)
        st1 = AbstractSyntaxTree(g.grammar.prods[10])
        st1.prod_id = 10
        st2 = AbstractSyntaxTree('+')
        st3 = AbstractSyntaxTree(g.grammar.prods[10])
        st3.prod_id = 10
        st4 = AbstractSyntaxTree(g.grammar.prods[6])
        st4.prod_id = 6
        st4.desc[1] = AbstractSyntaxTree(g.grammar.prods[10])
        st4.desc[1].prod_id = 10
        st4.desc[2] = AbstractSyntaxTree(g.grammar.prods[8])
        st4.desc[2].prod_id = 8

        print(st1)
        print(st2)
        print(st3)
        print(st4)

        stack = [st1, st2, st4, st3, st4, st4]
        mobj = GraphvizGraph(lr_stack_to_graphviz(stack, g.grammar))
        self.add(mobj)
        """
        # Adding nodes while building the tree itself is very important 
        # This we the nodes are always correctly numbered for graphviz
        curr_node_id = 0
        g = LR1Parser(GRAMMAR)
=======
        """
        g = LR1Parser(GRAMMAR)
        st1 = AbstractSyntaxTree(g.grammar.prods[10])
        st1.prod_id = 10
        st2 = AbstractSyntaxTree('+')
        st3 = AbstractSyntaxTree(g.grammar.prods[10])
        st3.prod_id = 10
        st4 = AbstractSyntaxTree(g.grammar.prods[6])
        st4.prod_id = 6
        st4.desc[1] = AbstractSyntaxTree(g.grammar.prods[10])
        st4.desc[1].prod_id = 10
        st4.desc[2] = AbstractSyntaxTree(g.grammar.prods[8])
        st4.desc[2].prod_id = 8

        print(st1)
        print(st2)
        print(st3)
        print(st4)

        stack = [st1, st2, st4, st3, st4, st4]
        mobj = GraphvizGraph(lr_stack_to_graphviz(stack, g.grammar))
        self.add(mobj)
        """
        g = LR1Parser(GRAMMAR)
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
        string = [x.strip() for x in STRING.split(' ')]
        if string[-1] != '$':
            string.append('$')
        stack = [0]
        prev_mobject = None
        curr_mobject = None
        while True:
            top = stack[-1]
            a = string[0]
            entry = g.parsing_table.at[top, (ACTION, a)]
            if entry == ERROR:
                print('Parse error')
                raise ValueError('ERROR entry for top = {}, a = {}'.format(top, a))
            if isinstance(entry, list):
                # TODO: maybe allow preference in case of SR conflict ?
                entry = entry[0]
            if entry[0] == 's':
<<<<<<< HEAD
                t = AbstractSyntaxTree(a)
                t.node_id = curr_node_id
                curr_node_id += 1
                stack.append(t)
=======
                stack.append(AbstractSyntaxTree(a))
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
                stack.append(int(entry[1:]))
                string.pop(0)
            elif entry[0] == 'r':
                prod_id = int(entry[1:])
                prod = g.grammar.prods[prod_id]
                new_tree = AbstractSyntaxTree(prod.lhs)
                new_tree.prod_id = prod_id
<<<<<<< HEAD
                new_tree.node_id = curr_node_id
                curr_node_id += 1
=======
>>>>>>> 5706e3714db65e258e447176a1589c366bc97d5f
                # I'm getting the popped list and then traversing it in
                # reverse fashion again
                # TODO: can this be optimized ?
                popped_list = []
                if prod.rhs[0] != EPSILON:
                    for _ in range(len(prod.rhs)):
                        if not stack:
                            raise ValueError()
                        stack.pop(-1)
                        if not stack:
                            raise ValueError()
                        popped_list.append(stack.pop(-1))
                else:
                    new_tree.desc.append(AbstractSyntaxTree(EPSILON))
                for i in range(len(popped_list)-1, -1, -1):
                    new_tree.desc.append(popped_list[i])
                new_top = stack[-1]
                nonterminal = prod.lhs
                new_state = g.parsing_table.at[new_top, (GOTO, nonterminal)]
                stack.append(new_tree)
                if isinstance(new_state, list):
                    new_state = new_state[0]
                stack.append(int(new_state))
            elif entry == ACCEPT:
                prod = g.grammar.prods[0]
                assert prod.rhs[-1] == '$' and len(prod.rhs) == 2
                # parse successful
                curr_mobject = GraphvizGraph(lr_stack_to_graphviz(stack, g.grammar))
                self.play(*transform_graphviz_graphs(prev_mobject, curr_mobject))
                break
            else:
                raise ValueError('Unknown Error')
                break
            curr_mobject = GraphvizGraph(lr_stack_to_graphviz(stack, g.grammar))
            if prev_mobject is not None:
                self.play(*transform_graphviz_graphs(prev_mobject, curr_mobject))
                self.remove(prev_mobject)
            else:
                self.add(curr_mobject)
            prev_mobject = curr_mobject

        return
        g1 = pgv.AGraph('expr1.dot')
        # calling the layout function is important
        g1.layout('dot')
        #print(g1.string())
        g2 = pgv.AGraph('expr2.dot')
        # calling the layout function is important
        g2.layout('dot')
        
        mobj_g1 = GraphvizGraph(g1)
        mobj_g2 = GraphvizGraph(g2)
        self.add(mobj_g1)
        self.wait(1)
        # self.play(Transform(mobj_g1, mobj_g2))
        self.play(*transform_graphviz_graphs(mobj_g1, mobj_g2))
        self.wait(1)
        """
        g = LR1Parser(GRAMMAR)
        print(g.grammar.prods[8])
        print(g.grammar.prods[2])
        stack = [
            AbstractSyntaxTree(g.grammar.prods[8]),
            AbstractSyntaxTree('+'),
            AbstractSyntaxTree(g.grammar.prods[2])
        ]
        self.add(GraphvizGraph(lr_stack_to_graphviz(stack, g.grammar)))
        """
