try:
    from manimlib import *
    manimce = False
except:
    from manim import *
    manimce = True
import logging
import os 
import sys 
from copy import deepcopy 
import yaml
from yacv.grammar import Grammar
from yacv.utils import setup_logger, get_manim_config
from yacv.ll1 import LL1Parser
from yacv.lr import LR0Parser, SLR1Parser, LALR1Parser, LR1Parser
from yacv.vis import LL1ParsingVisualizer, LRParsingVisualizer
parser_map = {
    'll1'  : LL1Parser,
    'lr0'  : LR0Parser,
    'slr1' : SLR1Parser,
    'lalr1': LALR1Parser,
    'lr1'  : LR1Parser
}

ROOT_DIR = 'yacv_{grammar}'
HELP_MESSAGE = """-------------------------------------
yacv: Yet Another Compiler Visualizer
-------------------------------------
usage: yacv <path/to/config/file>

-------------------------------------
Project URL : https://github.com/ashutoshbsathe/yacv
Config spec : https://ashutoshbsathe.github.io/yacv/config 
"""
def parse_args():
    class Namespace(object):
        def __init__(self, **kwargs):
            choices = {
                'parsing_algo': ['ll1', 'lr0', 'slr1', 'lr1', 'lalr1'],
                'manim_video_quality': ['480p', '720p', '1080p', '1440p', '2160p']
            }
            store_true = ['vis_tree', 'vis_parsing', 'vis_automaton', 'parsing_table']
            for k, v in kwargs.items():
                key = k.replace('-', '_')
                if key in choices and v not in choices[key]:
                    raise ValueError('Incorrect config value. Attribute {} must be one out of {}, received "{}"'.format(k, choices[key], v))
                if key in store_true:
                    v = bool(v)
                self.__dict__[k.replace('-','_')] = v
            for k in store_true:
                if not hasattr(self, k):
                    self.__dict__[k] = False 
            if not hasattr(self, 'manim_video_quality'):
                self.manim_video_quality = '480p'
            if not hasattr(self, 'grammar') or not hasattr(self, 'string'):
                raise ValueError('Please specify both grammar and string in config')

        def __str__(self):
            ret = 'Namespace(\n'
            for k, v in self.__dict__.items():
                ret += '\t{} : {}\n'.format(k, v)
            ret += ')\n'
            return ret
    if len(sys.argv) != 2:
        print(HELP_MESSAGE, file=sys.stderr)
        sys.exit(1)
    args = yaml.safe_load(open(sys.argv[1]).read())
    return Namespace(**args)

def main():
    global ROOT_DIR
    setup_logger()
    log = logging.getLogger('yacv')
    args = parse_args()
    colors = args.colors if hasattr(args, 'colors') else None
    if not args.grammar or not args.string:
        log.fatal('Please provide both grammar and string') 
        exit(1)
    if args.parsing_algo == 'll1' and args.vis_automaton:
        log.fatal('LR state automaton does not exist for LL(1) parsing')
        exit(1)
    log.info('Using {} parsing algorithm'.format(
        args.parsing_algo.upper()))
    p = parser_map[args.parsing_algo](args.grammar)

    # Prepare the main directories
    grammar = ''.join(args.grammar.split('/')[-1].split('.')[:-1])
    ROOT_DIR = ROOT_DIR.format(grammar=grammar)
    folder = os.path.join(ROOT_DIR, args.parsing_algo)
    os.makedirs(folder, exist_ok=True)
    if args.parsing_table:
        fname = '{}-parsing-table.csv'.format(args.parsing_algo)
        p.parsing_table.to_csv(os.path.join(folder, fname))
        log.info('Parsing table exported to {}'.format(os.path.join(folder, fname)))
    if args.vis_automaton:
        fname = '{}-state-automaton.pdf'.format(args.parsing_algo)
        G = p.visualize_automaton()
        G.draw(os.path.join(folder, fname))
        log.info('LR automaton visualized at {}'.format(os.path.join(folder, fname)))
    string = args.string.split(' ')
    string = [x.strip() for x in string]
    string = [x for x in string if x]
    if string[-1] != '$':
        string.append('$')
    if args.vis_tree:
        string_folder = ''.join(string)
        string_folder = os.path.join(folder, string_folder)
        os.makedirs(string_folder, exist_ok=True)
        fname = 'abstractsyntaxtree.pdf'
        G = p.visualize_syntaxtree(deepcopy(string), colors)
        G.draw(os.path.join(string_folder, fname))
        log.info('Syntax tree visualized to {}'.format(os.path.join(folder, fname)))
    if args.vis_parsing:
        string_folder = ''.join(string)
        string_folder = os.path.join(folder, string_folder)
        os.makedirs(string_folder, exist_ok=True)
        fname = 'ManimParsingVisualization'
        manim_config = get_manim_config(string_folder, fname, \
                args.manim_video_quality)
        if manimce:
            from manim import config 
            for k, v in manim_config.items():
                config[k] = v
            kwargs = {}
        else:
            kwargs = manim_config 
        vis = LL1ParsingVisualizer(**kwargs) if args.parsing_algo == \
                'll1' else LRParsingVisualizer(**kwargs)
        vis.setup(p, deepcopy(string), colors)
        if manimce:
            vis.render()
        else:
            vis.run()
    log.info('YACV finished')
    return 

if __name__ == '__main__':
    main()
