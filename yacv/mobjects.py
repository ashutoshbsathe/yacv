try:
    from manimlib import *
    manimce = False 
except ImportError as e:
    from manim import *
    manimce = True
import numpy as np 
import pygraphviz as pgv
import logging 
from yacv.abstractsyntaxtree import AbstractSyntaxTree
from yacv.grammar import *
from yacv.ll1 import *
from yacv.lr import *
from yacv.constants import *
from yacv.utils import *
class GraphvizMobject(VGroup):
    # do note that graph must have .layout() called on it already
    def __init__(self, graph, **kwargs):
        # digest_config doesn't work in ManimCE
        # digest_config(self, kwargs, locals())
        super().__init__(**kwargs)
        self.new_bbox = None
        self.scale_x = None
        self.scale_y = None 
        x, y, l, w = graph.graph_attr['bb'].split(',')
        self.bounding_box = [float(x), float(y), float(l), float(w)]
        self.nodes = {}
        self.edges = {}
        self.graph_added = False 
        self.add_graph(graph) 

    # Manim grid is only 14x8, we need to fit the graphviz graph in this
    def gridify(self, x, y):
        log = logging.getLogger('yacv')
        assert self.bounding_box is not None and len(self.bounding_box) == 4
        global YACV_MANIM_MAX_AST_HEIGHT, YACV_MANIM_MAX_AST_WIDTH
        bounding_box = self.bounding_box
        if self.new_bbox is None:
            width = bounding_box[2] - bounding_box[0]
            height = bounding_box[3] - bounding_box[1]
            ratio = width / height 
            # Find the maximum bbox that fits the screen "nicely"
            new_bbox = (0, 0)
            for new_height in np.linspace(1.0, YACV_MANIM_MAX_AST_HEIGHT, num=100):
                new_width = ratio * new_height 
                if new_width <= YACV_MANIM_MAX_AST_WIDTH:
                    new_bbox = (new_width, new_height) 
            new_width, new_height = new_bbox
            new_bbox = [-new_width/2, -new_height/2, new_width/2, new_height/2]
            self.scale_x = new_width / width 
            self.scale_y = new_height / height 
            self.new_bbox = new_bbox 
            log.debug('New bbox = {}'.format(self.new_bbox))
        assert self.scale_x is not None and self.scale_y is not None 
        new_x = self.new_bbox[0] + self.scale_x * float(x) 
        new_y = self.new_bbox[1] + self.scale_y * float(y) 
        log.debug('({},{}) -> ({},{})'.format(x, y, new_x, new_y))
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

    def add_graph(self, graph):
        log = logging.getLogger('yacv')
        if self.graph_added:
            # TODO: warn the user about already added graph via loggers
            return
        g = graph
        for n in g.nodes():
            # TODO: Can we potentially make this easy to read ?
            replacement = '$\\epsilon$' if manimce else '\\epsilon'
            label = prepare_text(n.attr['label'])
            label = label.replace('&#x3B5;', replacement)
            dot = Tex('{{' + label + '}}')
            x, y = n.attr['pos'].split(',')
            log.debug('Label = {}'.format(label))
            x, y = self.gridify(x, y)
            dot.move_to(x*RIGHT + y*UP)
            if n.attr['fontcolor']:
                dot.set_color(n.attr['fontcolor'])
            dot.scale(YACV_MANIM_TEXT_SCALE)
            self.add(dot)
            self.nodes[str(n)] = dot 
            log.debug('End of iteration for adding a node')
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
            log.debug('End of iteration for adding an edge')
        self.graph_added = True 

def transform_graphviz_graphs(old, new):
    log = logging.getLogger('yacv')
    common_nodes = set(old.nodes.keys()).intersection(set(new.nodes.keys()))
    common_edges = set(old.edges.keys()).intersection(set(new.edges.keys()))
    log.debug('Common nodes = {}'.format(common_nodes))
    log.debug('Common edges = {}'.format(common_edges))
    anims = []

    def is_equiv_vertices(n):
        # manimce does not strip the extra {{ }} from the latex
        if manimce:
            return int(n) < 0 or old.nodes[n].tex_string[2] == \
                new.nodes[n].tex_string[2]
        else:
            return int(n) < 0 or old.nodes[n].tex_string[0] == \
                new.nodes[n].tex_string[0]

    for n in list(common_nodes):
        if is_equiv_vertices(n):
            anims.append(ReplacementTransform(old.nodes[n], new.nodes[n]))
            log.debug('Transforming from {} to {}'.format(old.nodes[n].get_center(), new.nodes[n].get_center()))
        else:
            anims.append(FadeOut(old.nodes[n]))
            anims.append(FadeIn(new.nodes[n]))

    for e in list(common_edges):
        u, v = e[1:-1].split(',')
        if is_equiv_vertices(u) and is_equiv_vertices(v):
            anims.append(ReplacementTransform(old.edges[e], new.edges[e]))
        else:
            anims.append(FadeOut(old.edges[e]))
            anims.append(FadeIn(new.edges[e]))

    old_nodes = set(old.nodes.keys()).difference(common_nodes)
    old_edges = set(old.edges.keys()).difference(common_edges)
    log.debug('Old nodes = {}'.format(old_nodes))
    log.debug('Old edges = {}'.format(old_edges))
    for n in list(old_nodes):
        log.debug('Fading out {}'.format(old.nodes[n].get_center()))
        anims.append(FadeOut(old.nodes[n]))

    for e in list(old_edges):
        anims.append(FadeOut(old.edges[e]))

    new_nodes = set(new.nodes.keys()).difference(common_nodes)
    new_edges = set(new.edges.keys()).difference(common_edges)
    log.debug('New nodes = {}'.format(new_nodes))
    log.debug('New edges = {}'.format(new_edges))
    for n in list(new_nodes):
        log.debug('Fading in {}'.format(new.nodes[n].get_center()))
        anims.append(FadeIn(new.nodes[n]))

    for e in list(new_edges):
        anims.append(FadeIn(new.edges[e]))

    return anims 

def ast_to_graphviz(ast, grammar, colors=None):
    global YACV_GRAPHVIZ_COLORS
    if colors:
        YACV_GRAPHVIZ_COLORS = colors
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
            color = YACV_GRAPHVIZ_COLORS[top.prod_id % len(YACV_GRAPHVIZ_COLORS)]
            G.get_node(node).attr['fontcolor'] = color 
        desc_ids = []
        for desc in top.desc:
            if desc.root == YACV_EPSILON:
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
                    weight=YACV_GRAPHVIZ_INFINITY)

    return G, terminal_nodes 

def stack_to_graphviz(stack, grammar, colors=None):
    prod_subgraphs = []
    terminal_nodes = []
    root_nodes = []
    ret = pgv.AGraph(name='AbstractSyntaxForest', directed=True)
    for item in stack:
        if not isinstance(item, AbstractSyntaxTree):
            continue 
        if len(item.desc) > 1:
            root_nodes.append(item.node_id)
        g, t_nodes = ast_to_graphviz(item, grammar, colors) 
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
                prod.add_edge(e[0], e[1], style='invis', weight=YACV_GRAPHVIZ_INFINITY)

    # Finally, add the subgraph containing all the terminals 
    term = ret.add_subgraph(terminal_nodes, name='Terminals')
    term.graph_attr['rank'] = 'sink' 
    for i in range(len(term.nodes())-1):
        term.add_edge(terminal_nodes[i], terminal_nodes[i+1], style='invis', \
                weight=YACV_GRAPHVIZ_INFINITY)

    ret.edge_attr['dir'] = 'none'
    ret.node_attr['ordering'] = 'out'
    ret.node_attr['height'] = 0 
    ret.node_attr['width'] = 0
    ret.node_attr['margin'] = 0.1
    ret.node_attr['shape'] = 'none'

    ret.layout('dot')
    ret.draw('sample.png')
    return ret

def coord(x, y, z=0):
    return np.array([x, y, z])

class StackMobject(VGroup):
    def __init__(self, stack=None, **kwargs):
        # digest_config doesn't work in CE
        # digest_config(self, kwargs, locals())
        super().__init__(**kwargs)
        bottom_line = Line(start=[-6, -3, 0], end=[-5, -3, 0])
        left_line = Line(start=[-6, -3, 0], end=[-6, 2, 0])
        right_line = Line(start=[-5, -3, 0], end=[-5, 2, 0])
        bottom_text = Tex('\\dots')
        bottom_text.next_to(bottom_line, UP)
        self.add(bottom_line)
        self.add(left_line)
        self.add(right_line)
        self.add(Line(start=[-5, -3, 0], end=[-5, 2, 0]))
        self.bottom = bottom_line 
        self.left = left_line 
        self.right = right_line 

        self.elements = {}
        prev_mobject = self.bottom
        if stack is not None:
            self.stack_len = len(stack)
            if self.stack_len > YACV_MANIM_MAX_STACK_VIS:
                self.remove(bottom_line)
                self.add(bottom_text)
                self.bottom = bottom_text
                prev_mobject = bottom_text
            if len(stack) > YACV_MANIM_MAX_STACK_VIS:
                start_idx = stack.index(stack[-YACV_MANIM_MAX_STACK_VIS])
            else:
                start_idx = 0
            stack = stack[-YACV_MANIM_MAX_STACK_VIS:]
            for i, elem in enumerate(stack):
                if isinstance(elem, AbstractSyntaxTree):
                    text = elem.root 
                else:
                    text = str(elem) 
                new_mobject = Tex(prepare_text(text))
                new_mobject.next_to(prev_mobject, UP)
                new_mobject.scale(YACV_MANIM_TEXT_SCALE)
                self.add(new_mobject)
                prev_mobject = new_mobject
                self.elements[start_idx + i] = new_mobject 
        prev_mobject.set_color(RED)
        self.arrow = Tex('$\\downarrow$') if manimce else Tex('\\downarrow')
        self.arrow.next_to(prev_mobject, UP)
        self.arrow.set_color(RED)
        self.add(self.arrow)

        self.indicator = Tex('Stack')
        self.indicator.next_to(self.bottom, DOWN)
        self.indicator.scale(YACV_MANIM_TEXT_SCALE)
        self.add(self.indicator)

def transform_stacks(old, new):
    # Should we animate the bottom_line ?
    anims = []
    anims.append(ReplacementTransform(old.left, new.left))
    anims.append(ReplacementTransform(old.right, new.right))
    anims.append(ReplacementTransform(old.bottom, new.bottom))
    common_idx = set(old.elements.keys()).intersection(new.elements.keys())
    old_idx = set(old.elements.keys()).difference(common_idx)
    new_idx = set(new.elements.keys()).difference(common_idx)
    for i in common_idx:
        anims.append(ReplacementTransform(old.elements[i], new.elements[i]))

    for i in old_idx:
        anims.append(FadeOut(old.elements[i]))

    for i in new_idx:
        anims.append(FadeIn(new.elements[i]))
    min_idx = min(old.elements.keys())
    for i in new_idx:
        if i > min_idx:
            anims.append(Flash(new.elements[i], color=GREEN))
    anims.append(ReplacementTransform(old.arrow, new.arrow))
    anims.append(ReplacementTransform(old.indicator, new.indicator))
    return anims
