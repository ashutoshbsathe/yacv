import argparse
import logging 
from utils import setup_logger, YACVError 
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
            choices=['480p', '720p', '1080p', '1440p'], \
            help='Video quality for manim rendering')
    args = parser.parse_args()
    return args

def main():
    setup_logger()
    log = logging.getLogger('yacv')
    args = parse_args()
    if not args.grammar or not args.string:
        log.fatal('Please provide both grammar and string') 
        exit(1)
    return

if __name__ == '__main__':
    main()
