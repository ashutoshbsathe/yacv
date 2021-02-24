from manimlib import *
import numpy as np 
import pygraphviz as pgv
from abstractsyntaxtree import AbstractSyntaxTree
from grammar import *
from ll1 import *
from lr import *
MAX_AST_WIDTH  = 10
MAX_AST_HEIGHT = 7
class GraphvizMobject(VGroup):
    # do note that graph must have .layout() called on it already
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

    # Manim grid is only 14x8, we need to fit the graphviz graph in this
    def gridify(self, x, y):
        assert self.bounding_box is not None and len(self.bounding_box) == 4
        global MAX_AST_HEIGHT, MAX_AST_WIDTH
        bounding_box = self.bounding_box
        if self.new_bbox is None:
            width = bounding_box[2] - bounding_box[0]
            height = bounding_box[3] - bounding_box[1]
            ratio = width / height 
            # Find the maximum bbox that fits the screen "nicely"
            new_bbox = (0, 0)
            for new_height in np.linspace(1.0, MAX_AST_HEIGHT, num=100):
                new_width = ratio * new_height 
                if new_width <= MAX_AST_WIDTH:
                    new_bbox = (new_width, new_height) 
            new_width, new_height = new_bbox
            new_bbox = [-new_width/2, -new_height/2, new_width/2, new_height/2]
            self.scale_x = new_width / width 
            self.scale_y = new_height / height 
            self.new_bbox = new_bbox 
            print(self.new_bbox)
        assert self.scale_x is not None and self.scale_y is not None 
        new_x = self.new_bbox[0] + self.scale_x * float(x) 
        new_y = self.new_bbox[1] + self.scale_y * float(y) 
        print('({},{}) -> ({},{})'.format(x, y, new_x, new_y))
        return new_x, new_y 

    # https://codereview.stackexchange.com/questions/240710/pure-python-b%C3%A9zier-curve-implementation
    # I'm not sure how the internal manim bezier is written so cannot test it 
    def bezier_curve(self, control_points, n=11):
        return [
            self.bezier_point(control_points, t)
            for t in (
                i * 1. / (n - 1) for i in range(n)
            )
        ]

    def bezier_point(self, control_points, t):
        if len(control_points) == 1:
            result, = control_points
            return result 
        control_linestring = zip(control_points[:-1], control_points[1:])
        return self.bezier_point([
            (1 - t) * p1 + t * p2 for p1, p2 in control_linestring
        ], t)

    def coord(self, x, y, z=0):
        return np.array([x, y, z])

    def add_graph(self):
        if self.graph_added:
            # TODO: warn the user about already added graph via loggers
            return
        g = self.graph 
        for n in g.nodes():
            label = n.attr['label'].replace('&#x3B5;', '\epsilon')
            dot = Tex('{{' + label + '}}')
            x, y = n.attr['pos'].split(',')
            print(label)
            x, y = self.gridify(x, y)
            dot.move_to(x*RIGHT + y*UP)
            if n.attr['fontcolor']:
                dot.set_color(n.attr['fontcolor'])
            self.add(dot)
            self.nodes[str(n)] = dot 
            print(64 * '-')
        for e in g.edges():
            if e.attr['style'] == 'invis':
                continue 
            points = [np.asarray(self.gridify(*x.split(',')[-2:]))\
                    for x in e.attr['pos'].split(' ')]
            # We call bezier on the "gridified" points
            # TODO: will it be more accurate to use raw coords ?
            bezier_pts = self.bezier_curve(points, n=101)
            bezier_pts = [self.coord(*x) for x in bezier_pts]
            path = VMobject()
            path.set_points_smoothly(bezier_pts)
            if e.attr['color']:
                path.set_color(e.attr['color'])
            self.add(path)
            key = '(' + str(e[0]) + ',' + str(e[1]) + ')'
            self.edges[key] = path 
            print(64*'-')
        self.graph_added = True 

def transform_graphviz_graphs(old, new):
    common_nodes = set(old.nodes.keys()).intersection(set(new.nodes.keys()))
    common_edges = set(old.edges.keys()).intersection(set(new.edges.keys()))
    print('Common nodes = {}'.format(common_nodes))
    print('Common edges = {}'.format(common_edges))
    anims = []

    def is_equiv_vertices(n):
        return int(n) < 0 or old.graph.get_node(n).attr['label'][0] == \
                new.graph.get_node(n).attr['label'][0] 

    for n in list(common_nodes):
        if is_equiv_vertices(n):
            anims.append(Transform(old.nodes[n], new.nodes[n]))
            print('Transforming from {} to {}'.format(old.nodes[n].get_center(), new.nodes[n].get_center()))
        else:
            anims.append(FadeOut(old.nodes[n]))
            anims.append(FadeIn(new.nodes[n]))

    for e in list(common_edges):
        u, v = e[1:-1].split(',')
        if is_equiv_vertices(u) and is_equiv_vertices(v):
            anims.append(Transform(old.edges[e], new.edges[e]))
        else:
            anims.append(FadeOut(old.edges[e]))
            anims.append(FadeIn(new.edges[e]))

    old_nodes = set(old.nodes.keys()).difference(common_nodes)
    old_edges = set(old.edges.keys()).difference(common_edges)
    print('Old nodes = {}'.format(old_nodes))
    print('Old edges = {}'.format(old_edges))
    for n in list(old_nodes):
        print('Fading out {}'.format(old.nodes[n].get_center()))
        anims.append(FadeOut(old.nodes[n]))

    for e in list(old_edges):
        anims.append(FadeOut(old.edges[e]))

    new_nodes = set(new.nodes.keys()).difference(common_nodes)
    new_edges = set(new.edges.keys()).difference(common_edges)
    print('New nodes = {}'.format(new_nodes))
    print('New edges = {}'.format(new_edges))
    for n in list(new_nodes):
        print('Fading in {}'.format(new.nodes[n].get_center()))
        anims.append(FadeIn(new.nodes[n]))

    for e in list(new_edges):
        anims.append(FadeIn(new.edges[e]))

    return anims 

def ast_to_graphviz(ast, grammar):
    G = pgv.AGraph(name='AST{}'.format(ast.node_id), directed=True)
    stack = [ast]
    prods = []
    while stack:
        top = stack.pop(0)
        node = top.node_id 
        assert node is not None 
        if str(node) not in G.nodes():
            G.add_node(node, label=top.root)
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
            G.add_edge(node, desc.node_id, color=color)
            desc_ids.append(desc.node_id)
            stack.append(desc) 
        prods.append(desc_ids)

    # Figure out terminal nodes 
    # DFS is important to keep the order of temrinal nodes proper
    terminal_nodes = []
    stack = [G.nodes()[0]]
    visited = []
    terminals = grammar.terminals 
    while stack:
        node = stack.pop(-1)
        if node not in visited:
            visited.append(node)
            if node.attr['label'] in terminals:
                terminal_nodes.append(node) 
            for i in range(len(G.successors(node))-1, -1, -1):
                stack.append(G.successors(node)[i])

    # Fix the alignment of productions
    for i, prod in enumerate(prods):
        nonterminals = []
        for node_id in prod:
            if G.get_node(node_id).attr['label'] in terminals:
                continue 
            nonterminals.append(G.get_node(node_id))
        if len(nonterminals) <= 1:
            continue 
        nt = G.subgraph(nonterminals, name='Prod{}G{}'.format(i, ast.node_id))
        nt.graph_attr['rank'] = 'same'
        for j in range(len(nt.nodes())-1):
            nt.add_edge(nonterminals[j], nonterminals[j+1], style='invis', \
                    weight=INFINITY)

    return G, terminal_nodes 

def stack_to_graphviz(stack, grammar):
    prod_subgraphs = []
    terminal_nodes = []
    root_nodes = []
    ret = pgv.AGraph(name='AbstractSyntaxForest', directed=True)
    for item in stack:
        if not isinstance(item, AbstractSyntaxTree):
            continue 
        if len(item.desc) > 1:
            root_nodes.append(item.node_id)
        g, t_nodes = ast_to_graphviz(item, grammar) 
        terminal_nodes.extend(t_nodes) 

        for n in g.nodes():
            ret.add_node(n)
            for k in n.attr.keys():
                ret.get_node(n).attr[k] = n.attr[k]

        for e in g.edges():
            ret.add_edge(e)
            for k in e.attr.keys():
                ret.get_edge(e[0], e[1]).attr[k] = e.attr[k]

        for graph in g.subgraphs():
            prod = ret.add_subgraph(graph.nodes(), name=graph.name)
            prod.graph_attr['rank'] = 'same'
            # I assume here that we don't need to add extra edges 
            # because I believe the subgraph edges are also added above 
            # Adding these just to be safe 
            # TODO: experiment with removing this once ?
            for e in graph.edges():
                prod.add_edge(e[0], e[1], style='invis', weight=INFINITY)

    # Finally, add the subgraph containing all the terminals 
    term = ret.add_subgraph(terminal_nodes, name='Terminals')
    term.graph_attr['rank'] = 'sink' 
    for i in range(len(term.nodes())-1):
        term.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis', \
                weight=INFINITY)

    ret.edge_attr['dir'] = 'none'
    ret.node_attr['ordering'] = 'out'
    ret.node_attr['height'] = 0 
    ret.node_attr['width'] = 0
    ret.node_attr['margin'] = 0.1
    ret.node_attr['shape'] = 'none'

    ret.layout('dot')
    ret.draw('sample.png')
    return ret

# Kanged from https://www.youtube.com/watch?v=gIvQsqXy5os&list=PL2B6OzTsMUrwo4hA3BBfS7ZR34K361Z8F&index=13
class Grid(VGroup):
    CONFIG = {
        "height": 6.0,
        "width": 6.0,
    }

    def __init__(self, rows, columns, **kwargs):
        digest_config(self, kwargs, locals())
        super().__init__(**kwargs)

        x_step = self.width / self.columns
        y_step = self.height / self.rows

        for x in np.arange(0, self.width + x_step, x_step):
            self.add(Line(
                [x - self.width / 2., -self.height / 2., 0],
                [x - self.width / 2., self.height / 2., 0],
            ))
        for y in np.arange(0, self.height + y_step, y_step):
            self.add(Line(
                [-self.width / 2., y - self.height / 2., 0],
                [self.width / 2., y - self.height / 2., 0]
            ))


class ScreenGrid(VGroup):
    CONFIG = {
        "rows": 8,
        "columns": 14,
        "height": FRAME_Y_RADIUS * 2,
        "width": 14,
        "grid_stroke": 0.5,
        "grid_color": WHITE,
        "axis_color": RED,
        "axis_stroke": 2,
        "labels_scale": 0.25,
        "labels_buff": 0,
        "number_decimals": 2
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        rows = self.rows
        columns = self.columns
        grid = Grid(width=self.width, height=self.height, rows=rows, columns=columns)
        grid.set_stroke(self.grid_color, self.grid_stroke)

        vector_ii = ORIGIN + np.array((- self.width / 2, - self.height / 2, 0))
        vector_si = ORIGIN + np.array((- self.width / 2, self.height / 2, 0))
        vector_sd = ORIGIN + np.array((self.width / 2, self.height / 2, 0))

        axes_x = Line(LEFT * self.width / 2, RIGHT * self.width / 2)
        axes_y = Line(DOWN * self.height / 2, UP * self.height / 2)

        axes = VGroup(axes_x, axes_y).set_stroke(self.axis_color, self.axis_stroke)

        divisions_x = self.width / columns
        divisions_y = self.height / rows

        directions_buff_x = [UP, DOWN]
        directions_buff_y = [RIGHT, LEFT]
        dd_buff = [directions_buff_x, directions_buff_y]
        vectors_init_x = [vector_ii, vector_si]
        vectors_init_y = [vector_si, vector_sd]
        vectors_init = [vectors_init_x, vectors_init_y]
        divisions = [divisions_x, divisions_y]
        orientations = [RIGHT, DOWN]
        labels = VGroup()
        set_changes = zip([columns, rows], divisions, orientations, [0, 1], vectors_init, dd_buff)
        for c_and_r, division, orientation, coord, vi_c, d_buff in set_changes:
            for i in range(1, c_and_r):
                for v_i, directions_buff in zip(vi_c, d_buff):
                    ubication = v_i + orientation * division * i
                    coord_point = round(ubication[coord], self.number_decimals)
                    label = Text(f"{coord_point}",font="Arial",stroke_width=0).scale(self.labels_scale)
                    label.next_to(ubication, directions_buff, buff=self.labels_buff)
                    labels.add(label)

        self.add(grid, axes, labels)

def coord(x, y, z=0):
    return np.array([x, y, z])
