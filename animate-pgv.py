import pygraphviz as pgv
from manimlib import *
import numpy as np
import sys
sys.path.append('/home/ashutosh/parser-vis')
from grammar import EPSILON
from ll1 import LL1Parser
from lr import LR0Parser, LR1Parser, SLR1Parser
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
STRING = 'id + id * id / id - ( id )'
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
        for n in g.nodes():
            label = n.attr['label'].replace('&#x3B5;', '\epsilon')
            print(label)
            dot = Tex('{{' + label + '}}')
            x, y = n.attr['pos'].split(',')
            x, y = self.gridify(x, y)
            dot.move_to(x*RIGHT + y*UP)
            dot.scale(0.5)
            self.add(dot)
        self.graph_added = True

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
            nt.add_edge(nonterminals[j], nonterminals[j+1], style='invis', \
                    weight=INFINITY)
    # Finally, add the terminal subgraphs
    t = G.add_subgraph(terminal_nodes, name='Terminals{}'.format(init_node))
    t.graph_attr['rank'] = 'max'
    for i in range(len(t.nodes())-1):
        t.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis')

    return G

def lr_stack_to_graphviz(stack, grammar):
    prod_subgraphs = []
    terminal_subgraphs = []
    forbidden_edges = []
    node_id = 0
    G = pgv.AGraph()
    for item in stack:
        if not isinstance(item, AbstractSyntaxTree):
            continue
        g = ast_to_graphviz(item, grammar, node_id)
        node_id += len(g.nodes())
        for n in g.nodes():
            G.add_node(n)
            for k in n.attr.keys():
                G.get_node(n).attr[k] = n.attr[k]
        for graph in g.subgraphs():
            if graph.name.startswith('Terminals'):
                terminal_subgraphs.append(graph)
                forbidden_edges.extend(graph.edges())
            elif graph.name.startswith('Production'):
                prod_subgraphs.append(graph)
                forbidden_edges.extend(graph.edges())

        for e in g.edges():
            if e in forbidden_edges:
                continue
            G.add_edge(e)
            print(e[0], e[1])
            for k in e.attr.keys():
                print(k, e.attr[k])
                G.get_edge(e[0], e[1]).attr[k] = e.attr[k]

    terminal_nodes = []
    for i in range(0, len(terminal_subgraphs)-1):
        # Add the i'th subgraph edges and then add the new one
        print('At graph {}'.format(i))
        tsub = terminal_subgraphs[i]
        print(tsub.nodes(), tsub.edges())
        for n in tsub.nodes():
            terminal_nodes.append(n)
            if n not in G.nodes():
                G.add_node(n)
        G.add_edges_from(tsub.edges())
        last_node = None
        visited = []
        """
        for n in tsub.nodes():
            print(n)
            
            if len(tsub.successors(n)) == 0:
                last_node = n
                break
            else:
                print(tsub.successors(n))
        """
        for e in tsub.edges():
            visited.append(str(e[0]))
        print(visited)
        total = set([str(x) for x in tsub.nodes()])
        last_node = list(total.difference(set(visited)))[0]
        print(last_node)
        next_tsub = terminal_subgraphs[i+1]
        first_node = None
        visited = []
        """
        for n in next_tsub.nodes():
            print(n)
            if len(tsub.predecessors(n)) == 0:
                first_node = n
                break
            else:
                print(tsub.predecessors(n))
        """
        for e in next_tsub.edges():
            visited.append(str(e[1]))
        total = set([str(x) for x in next_tsub.nodes()])
        first_node = list(total.difference(set(visited)))[0]
        print(first_node)
        print(last_node, first_node)
        if last_node is not None and first_node is not None:
            if first_node not in G.nodes():
                G.add_node(first_node)
            G.add_edge(last_node, first_node)
        exit(0)
    last_graph = terminal_subgraphs[-1]
    terminal_nodes.extend(last_graph.nodes())
    G.add_edges_from(last_graph.edges(), style='invis', weight=INFINITY)

    t = G.add_subgraph(terminal_nodes, name='Terminals')
    t.graph_attr['rank'] = 'max'
    # Start thinking about productions now
    for i, prod in enumerate(prod_subgraphs):
        nt = G.add_subgraph(prod.nodes(), name='Production{}'.format(i))
        nt.graph_attr['rank'] = 'same'
        nt.add_edges_from(prod.edges())
    print('Reached before dotting')
    G.layout('dot')
    G.draw('output.png')
    print('Returning G')
    return G


class AnimateGraphs(Scene):
    def construct(self):
        g1 = pgv.AGraph('graph1.dot')
        # calling the layout function is important
        g1.layout('dot')
        print(g1.string())
        g2 = pgv.AGraph('graph2.dot')
        # calling the layout function is important
        g2.layout('dot')
        
        mobj_g1 = GraphvizGraph(g1)
        mobj_g2 = GraphvizGraph(g2)
        """
        self.add(mobj_g1)
        self.wait(1)
        self.play(Transform(mobj_g1, mobj_g2))
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
