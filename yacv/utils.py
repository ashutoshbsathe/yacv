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
from yacv.constants import yacv_manimce_config, yacv_manim_config
class YACVError(Exception):
    pass

def prepare_text(x):
    if manimce:
        return '\\textbf{' + x.replace('$', '\\$') if \
                '\\$' not in x else x + '}'
    else:
        return x.replace('$', '\\$') if '\\$' not in x else x

def setup_logger():
    log = logging.getLogger('yacv')
    log.setLevel('INFO')
    log.addHandler(RichHandler())
    install()
    return

def get_manim_config(save_dir, fname, video_quality='480p'):
    video_config_map = {
        '480p': {
                'width' : 854,
                'height': 480,
                'fps'   : 30
            },
        '720p': {
                'width' : 1280,
                'height': 720,
                'fps'   : 60
            },
        '1080p': {
                'width' : 1920,
                'height': 1080,
                'fps'   : 60
            },
        '1440p': {
                'width' : 2560,
                'height': 1440,
                'fps'   : 60
            },
        '2160p': {
                'width' : 3840,
                'height': 2160,
                'fps'   : 60
            }
    }
    quality = video_config_map[video_quality]
    width, height = quality['width'], quality['height']
    fps = quality['fps']
    if manimce:
        config = yacv_manimce_config
        config['assets_dir'] = save_dir 
        config['media_dir'] = save_dir 
        config['output_file'] = fname 
        config['pixel_width'] = width 
        config['pixel_height'] = height 
        config['frame_rate'] = fps
        return config 
    else:
        config = yacv_manim_config 
        config['file_writer_config']['file_name'] = fname 
        config['file_writer_config']['output_directory'] = save_dir
        config['camera_config']['pixel_width'] = width 
        config['camera_config']['pixel_height'] = height 
        config['camera_config']['frame_rate'] = fps
        return config
