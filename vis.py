from manimlib import *
import pygraphviz as pgv
import numpy as np
import sys
sys.path.append('/home/ashutosh/parser-vis')
from ll1 import LL1Parser
from lr import LR0Parser, LR1Parser, SLR1Parser

GRAMMAR = 'll1-expression-grammar.txt'
STRING = 'id + id * id / id - ( id )'
Parser = LR1Parser
bounding_box = None
new_bbox = None

# This is required because graphviz puts the actual pixel measurements in 
# the output file. This is incompatible with manim's standard 14x8 grid
# This function lets us "center" the graphviz plot onto the manim's grid
def gridify(x, y):
    global bounding_box, new_bbox, scale_x, scale_y
    assert bounding_box is not None and len(bounding_box) == 4
    if new_bbox is None:
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
        print(ref_width, ref_height)
        new_bbox = [-ref_width/2, -ref_height/2, ref_width/2, ref_height/2]
        scale_x = ref_width / width
        scale_y = ref_height / height
    assert scale_x is not None and scale_y is not None
    new_x = new_bbox[0] + scale_x * float(x)
    new_y = new_bbox[1] + scale_y * float(y)
    return new_x, new_y

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

# https://codereview.stackexchange.com/questions/240710/pure-python-b%C3%A9zier-curve-implementation
def bezier_curve(control_points, n=1001):
    return [
        bezier_point(control_points, t)
        for t in (
            i * 1. / (n - 1) for i in range(n)
        )
    ]

def bezier_point(control_points, t):
    if len(control_points) == 1:
        result,  = control_points
        return result
    control_linestring = zip(control_points[:-1], control_points[1:])
    return bezier_point([
        (1 - t) * p1 + t * p2 for p1, p2 in control_linestring
    ], t)

class ParseTree(Scene):
    def construct(self):
        global bounding_box
        grid = ScreenGrid()
        p = Parser(GRAMMAR)
        st = [x.strip() for x in STRING.split(' ') if x]
        g = p.visualize_syntaxtree(st)
        x, y, l, w = g.graph_attr['bb'].split(',')
        bounding_box = [float(x), float(y), float(l), float(w)]
        print(x, y, l, w)
        self.add(grid)
        for e in g.edges():
            if e.attr['style'] == 'invis':
                continue
            points = [np.asarray(gridify(*x.split(','))) \
                    for x in e.attr['pos'].split(' ')]
            # By default, graphviz with "dot" engine will use the "pos" attribute
            # for drawing the SVG path wutg orioer SVG path commands
            # Manim cannot just draw a curve through these points because these
            # points are equivalent to Bazier control points for that path
            # So default functions like `set_points_as_corner` or `_smoothly`
            # will NOT work out of box
            # I found an implementation of bezier in manim too, but I'm too dumb
            # to make it work so I kanged one off the internet
            bezier_pts = bezier_curve(points)
            bezier_pts = [coord(*x) for x in bezier_pts]
            path = VMobject()
            path.set_points_smoothly(bezier_pts)
            path.set_color(e.attr['color'])
            self.add(path)
        for n in g.nodes():
            label = n.attr['label'].replace('&#x3B5;', '\epsilon')
            dot = Tex(label, color=n.attr['color'])
            x, y = n.attr['pos'].split(',')
            x, y = gridify(x, y)
            print('Adding {}, at ({},{})'.format(label, x, y))
            dot.move_to(x*RIGHT + y*UP)
            dot.scale(0.5)
            self.add(dot)

