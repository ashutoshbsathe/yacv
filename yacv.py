try:
    from manimlib import *
    manimce = False
except:
    from manim import *
    manimce = True
import argparse
import logging
import os 
from grammar import Grammar
from utils import setup_logger, get_manim_config
from ll1 import LL1Parser
from lr import LR0Parser, SLR1Parser, LALR1Parser, LR1Parser
from vis import LL1ParsingVisualizer, LRParsingVisualizer
parser_map = {
    'll1'  : LL1Parser,
    'lr0'  : LR0Parser,
    'slr1' : SLR1Parser,
    'lalr1': LALR1Parser,
    'lr1'  : LR1Parser
}

ROOT_DIR = 'yacv_{grammar}'

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--grammar', help='Path to text file containing grammar rules')
    parser.add_argument('--string', help='String to parse')
    parser.add_argument('--parsing-algo', default='lr1', \
            choices=['ll1', 'lr0', 'slr1', 'lr1', 'lalr1'], \
            help='Name of the parsing algorithm to use')
    parser.add_argument('--vis-tree', default=False, \
            action='store_true', help='Visualize syntaxtree') 
    parser.add_argument('--vis-automaton', default=False, \
            action='store_true', help='Visualize LR automaton') 
    parser.add_argument('--parsing-table', default=False, \
            action='store_true', help='Export parsing table')
    parser.add_argument('--vis-parsing', default=False, \
            action='store_true', \
            help='Visualize parsing process using manim')
    parser.add_argument('--manim-video-quality', default='480p', \
            choices=['480p', '720p', '1080p', '1440p', '2160p'], \
            help='Video quality for manim rendering')
    args = parser.parse_args()
    return args

def main():
    global ROOT_DIR
    setup_logger()
    log = logging.getLogger('yacv')
    args = parse_args()
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
    if string[-1] != '$':
        string.append('$')
    if args.vis_tree:
        string_folder = ''.join(string)
        string_folder = os.path.join(folder, string_folder)
        os.makedirs(string_folder, exist_ok=True)
        fname = 'abstractsyntaxtree.pdf'
        G = p.visualize_syntaxtree(string)
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
        vis.setup(p, string)
        if manimce:
            vis.render()
        else:
            vis.run()

    return

if __name__ == '__main__':
    main()
