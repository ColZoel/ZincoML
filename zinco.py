"""
Zinco pipeline main file. All the pieces come together here.
"""

import os
from __init__ import __version__
from utils.parse_config import load_config

print(f'\n\n                             Zinco ㎖\n'
      f'                ––––––––––––––––––––––––––––––––––\n'
      f'         🚀 AI Boosted Zinco Data Collection Pipeline 🚀\n'
      f'            📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚\n'
      f'                         Version {__version__}  \n'
      f'                ––––––––––––––––––––––––––––––––––\n\n')


def pipeline(path=None):
    """
    Zinco pipeline main function
    """
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')
    if path is None:
        path = load_config(config_path)['input_images']

    # Step 1: Image segmentation



    # Step 2: Text extraction