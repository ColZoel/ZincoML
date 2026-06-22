from __init__ import __version__
from pipe import *
from utils.config import *


if __name__ == '__main__':

    print(f'\n\n'
          f'                                Zinco㎖\n'
          f'                     🚀 AI Boosted Zinco Pipeline 🚀\n'
          f'                             Version {__version__}  \n'
          f'                  ––––––––––––––––––––––––––––––––––\n\n')

    config = load_config('main')
    if not horizontal():
        vertical(path=config['input_images'], output=config['output_type'], cores=config['cores'])

