import os

from catsup.options import g
from catsup.utils import mkdir


def add_slash(url):
    if '//' in url:
        return url.rstrip('/') + '/'
    return '/%s/' % url.strip('/')


def get_template():
    default_config_path = os.path.join(g.public_templates_path, 'config.json')
    return open(default_config_path, 'r').read()


def create_config_file(path=None):
    if path:
        os.chdir(path)

    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, 'config.json')

    if os.path.exists(config_path):
        from catsup.logger import logger
        logger.warning("Config file already exist.")
        exit(1)

    mkdir("posts")
    mkdir("static")

    template = get_template()

    with open(config_path, 'w') as f:
        f.write(template)

    print('Created a new config file.'
          'Please configure your blog by editing config.json')
