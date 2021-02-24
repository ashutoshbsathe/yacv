# only for being able to run via `manimgl`
import sys
sys.path.append('/home/ashutosh/parser-vis/')
from manimlib import *
import pygraphviz as pgv
import numpy as np
from ll1 import *
from lr import *
from mobjects import *
import argparse
from copy import deepcopy
manim_args = {}

class LRParsingVisualizer(Scene):
    def setup(self, grammar='expression-grammar.txt', string='id + id', **kwargs):
        # Add a parser type argument here in the future
        self.grammar = grammar 
        if isinstance(string, str):
            string = string.split(' ')
            string = [x for x in string if x]
        if string[-1] != '$':
            string.append('$')
        self.string = string 
        super().setup(**kwargs)

    def construct(self):
        # grid = ScreenGrid()
        # self.add(grid)
        p = LR1Parser(self.grammar)
        string = self.string 
        stack = [0]
        old_stack_mobject = None
        prev_mobject = None 
        curr_mobject = None 
        curr_node_id = 0 # Assigning the node ids as we build the tree 
        status_mobject  = Tex('START')
        status_pos = 5.5*LEFT + 3*UP
        string_mobject = Text('String: ' + ' '.join(string))
        string_pos = 0*LEFT + 3.5*DOWN
        string_mobject.move_to(string_pos)
        string_mobject.scale(0.5)
        status_mobject.move_to(status_pos)
        while True:
            top = stack[-1]
            a = string[0]
            entry = p.parsing_table.at[top, (ACTION, a)]
            if old_stack_mobject is None:
                old_stack_mobject = StackMobject(stack)
            if entry == ERROR:
                # TODO: Get better error messages here
                raise ValueError('Parsing error. Got ERROR entry for top = {}, a = {}'.format(top, a))
            if isinstance(entry, list):
                # TODO: Can we implement some precedence here ?
                # Like, if it's shift reduce conflict, user configures the 
                # default action ?
                # Shouldn't be difficult, I already have a provision for 
                # preferred action in `LRAutomatonState`
                entry = entry[0]
            # Actual parsing logic starts 
            if entry[0] == 's':
                t = AbstractSyntaxTree(a)
                t.node_id = curr_node_id 
                curr_node_id += 1
                stack.append(t)
                stack.append(int(entry[1:]))
                string.pop(0)
                # Starting Animation 
                new_status_mobject=Tex('SHIFT \\; {}'.format(int(entry[1:])))
                new_status_mobject.move_to(status_pos)
                self.play(ShowCreationThenDestructionAround(status_mobject))
                self.play(Transform(status_mobject, new_status_mobject))
                self.wait(1)
                self.remove(new_status_mobject)
                all_anims = []
                curr_stack_mobject = StackMobject(stack)
                anim_s = transform_stacks(old_stack_mobject,curr_stack_mobject)
                curr_mobject = GraphvizMobject(stack_to_graphviz(stack, \
                            p.grammar))
                if prev_mobject is not None:
                    anim_t = transform_graphviz_graphs(prev_mobject, \
                            curr_mobject)
                else:
                    anim_t = [ShowCreation(curr_mobject)]
                all_anims.extend(anim_s)
                all_anims.extend(anim_t)
                self.play(*all_anims)
                self.wait(1)
                self.remove(old_stack_mobject)
                if prev_mobject is not None:
                    self.remove(prev_mobject)
                old_stack_mobject = curr_stack_mobject
                prev_mobject = curr_mobject 
                # Ending Animation 
            elif entry[0] == 'r':
                prod_id = int(entry[1:])
                prod = p.grammar.prods[prod_id]
                new_tree = AbstractSyntaxTree(prod.lhs)
                new_tree.prod_id = prod_id 
                new_tree.node_id = curr_node_id 
                curr_node_id += 1
                
                # Starting animation 
                # highlight 2 * len(prod.rhs) elements on the stack 
                l = old_stack_mobject.stack_len
                to_highlight = 2*len(prod.rhs) if l > 2*len(prod.rhs) else l 
                keys = list(old_stack_mobject.elements.keys())
                anims = []
                for i in keys[-to_highlight:]:
                    anims.append(Indicate(old_stack_mobject.elements[i]))
                self.play(*anims)
                self.wait(1) 
                
                prod_text = '{} \\rightarrow'.format(prod.lhs)
                if prod.rhs[0] == EPSILON:
                    prod_text += ' \\epsilon'
                else:
                    prod_text += ' {}'.format(' '.join(prod.rhs))
                new_status_mobject = Tex(prod_text)
                new_status_mobject.move_to(status_pos)
                self.play(ShowCreationThenDestructionAround(status_mobject))
                self.play(Transform(status_mobject, new_status_mobject))
                # self.play(Transform(status_mobject, \
                #        new_status_mobject))
                self.wait(1)
                self.remove(new_status_mobject)
                # Ending animation

                # I'm getting the popped list and then traversing it in 
                # reverse direction again just so that memory references 
                # are proper
                # TODO: can this be optimized ?
                popped_list = []
                if prod.rhs[0] != EPSILON:
                    for _ in range(len(prod.rhs)):
                        if not stack:
                            raise ValueError('Parsing Error: Stack prematurely empty')
                        stack.pop(-1)
                        if not stack:
                            raise ValueError('Parsing Error: Stack prematurely empty')
                        popped_list.append(stack.pop(-1))
                else:
                    # Note here that we don't need to increment `curr_node_id`
                    # This is because `epsilon` nodes are merged with their 
                    # parents when converting AST to Graphviz
                    new_tree.desc.append(AbstractSyntaxTree(EPSILON))
                for i in range(len(popped_list)-1,-1,-1):
                    new_tree.desc.append(popped_list[i])
                # Starting Animation 
                curr_stack_mobject = StackMobject(stack)
                anims = transform_stacks(old_stack_mobject, curr_stack_mobject)
                self.play(*anims)
                self.wait(1)
                old_stack_mobject = curr_stack_mobject
                self.add(old_stack_mobject)
                # Ending Animation 
                new_top = stack[-1]
                nonterminal = prod.lhs 
                new_state = p.parsing_table.at[new_top, (GOTO, nonterminal)]
                stack.append(new_tree)
                if isinstance(new_state, list):
                    new_state = new_state[0]
                stack.append(int(new_state))
                # Starting Animation 
                all_anims = []
                curr_stack_mobject = StackMobject(stack)
                anim_s = transform_stacks(old_stack_mobject,curr_stack_mobject)
                curr_mobject = GraphvizMobject(stack_to_graphviz(stack, \
                        p.grammar))
                anim_t = transform_graphviz_graphs(prev_mobject, curr_mobject)
                all_anims.extend(anim_s)
                all_anims.extend(anim_t)
                self.play(*all_anims)
                self.wait(1)
                old_stack_mobject = curr_stack_mobject
                prev_mobject = curr_mobject 
                # Ending Animation 
            elif entry == ACCEPT:
                prod = p.grammar.prods[0]
                assert prod.rhs[-1] == '$' and len(prod.rhs) == 2
                # Parsing successful 
                # TODO: Log that parsing is successful 
                new_status_mobject = Tex("ACCEPT")
                new_status_mobject.move_to(status_pos)
                new_status_mobject.set_color(YELLOW)
                self.play(ShowCreationThenDestructionAround(status_mobject))
                self.play(Transform(status_mobject, new_status_mobject))
                self.remove(new_status_mobject)
                curr_mobject = GraphvizMobject(stack_to_graphviz(stack, \
                        p.grammar))
                anims = transform_graphviz_graphs(prev_mobject, curr_mobject)
                self.play(*anims)

                break 
            else:
                raise ValueError('Unknown error while parsing')
            new_string_mobject = Text('String: ' + ' '.join(string))
            new_string_mobject.move_to(string_pos)
            new_string_mobject.scale(0.5)
            self.play(Transform(string_mobject, new_string_mobject))
            self.remove(new_string_mobject)
        return 


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-w', action='store_true')
    parser.add_argument('-l', action='store_true')
    parser.add_argument('-o', action='store_true')
    args = parser.parse_args()
    print(args)
    """
    bme = BasicManimExample()
    bme.setup()
    bme.construct()
    """
    vis = LRParsingVisualizer()
    # vis.setup('expression-grammar.txt', 'id + id / id - ( id + id )')
    vis.setup('expression-grammar.txt', 'id + id')
    vis.construct()
