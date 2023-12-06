from __init__ import __version__
from pipe import *
from utils.config import *


if __name__ == '__main__':

    print(f'\n\n                             Zinco ㎖\n'
          f'                ––––––––––––––––––––––––––––––––––\n'
          f'         🚀 AI Boosted Zinco Data Collection Pipeline 🚀\n'
          f'            📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚🦑📚\n'
          f'                         Version {__version__}  \n'
          f'                ––––––––––––––––––––––––––––––––––\n\n')

    config = load_config('main')
    if not horizontal():
        vertical(path=config['input_images'], output=config['output_type'],
                 debug=config['debug'], cores=config['cores'])

