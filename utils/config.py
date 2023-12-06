import yaml
import os
from os import getenv
from dotenv import load_dotenv
from configparser import ConfigParser

load_dotenv()
palm_key = getenv("PALM_API_KEY")
os.environ["PALM_API_KEY"] = palm_key

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
llm_config = os.path.join(root, 'parsing', 'config.cfg')
llm_examples = os.path.join(root, 'parsing', 'examples.yaml')


def get_config(step):
    """
    Gets the config file path
    """
    if step == 'main':
        return os.path.join(root, 'config.yaml')
    if step == 'parsing':
        return os.path.join(root, 'parsing', 'config.cfg')
    else:
        raise ValueError(f'Invalid step: {step}')


def load_config(step):
    """
    Parses the config file
    """
    path = get_config(step)
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def inp(path):
    """
    Gets the input path from the config file
    """
    return load_config(path)['input_images']


def horizontal():
    """
    Gets the horizontal image segmentation config
    """
    return load_config('main')['horizontal_process']


def update(path, key, value):
    """
    Updates the config file
    """
    config = load_config(path)
    config[key] = value
    with open(path, 'w') as f:
        yaml.dump(config, f)


def set_llm_examples(config, examples):
    """
    Sets the LLM examples
    """
    cp = ConfigParser()
    cp.read(config)
    cp.set('components.llm.task.examples', 'path', str(examples))
    with open(config, 'w') as f:
        cp.write(f)

    return
