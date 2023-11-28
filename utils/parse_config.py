import yaml
import os

def get_config(step):
    """
    Gets the config file path
    """
    if step == 'main':
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')
    if step == 'parsing':
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'parsing', 'config.cfg')
    else:
        raise ValueError(f'Invalid step: {step}')


def load_config(path):
    """
    Parses the config file
    """
    with open(path, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    return config


def get_input(path):
    """
    Gets the input path from the config file
    """
    return load_config(path)['input_images']


def horizontal():
    """
    Gets the horizontal image segmentation config
    """
    return load_config(get_config('main'))['horizontal_process']

