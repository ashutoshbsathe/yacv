try:
    from manimlib import *
    manimce = False
except ImportError as e:
    from manim import *
    manimce = True
import logging
import os 
from rich.traceback import install
from rich.logging import RichHandler 

class YACVError(Exception):
    pass

def prepare_text(x):
    if manimce:
        return '\\textbf{' + x.replace('$', '\\$') if '\\$' not in x else x \
                + '}'
    else:
        return x.replace('$', '\\$') if '\\$' not in x else x

def setup_logger():
    log = logging.getLogger('yacv')
    log.setLevel('INFO')
    log.addHandler(RichHandler())
    install()
    return
