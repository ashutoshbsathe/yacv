try:
    from manimlib import *
    manimce = False
except ImportError as e:
    from manim import *
    manimce = True
import logging
import os 

def prepare_text(x):
    if manimce:
        return '\\textbf{' + x.replace('$', '\\$') if '\\$' not in x else x \
                + '}'
    else:
        return x.replace('$', '\\$') if '\\$' not in x else x
