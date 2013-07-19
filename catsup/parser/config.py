import os
import sys

from tornado.util import ObjectDict
from tornado.escape import json_decode
from parguments.cli import prompt, prompt_bool

from catsup.logger import logger
from catsup.options import g
from catsup.utils import update_nested_dict, urljoin

from .utils import add_slash

import catsup.themes


def get_template():
    default_config_path = os.path.join(g.public_templates_path, 'config.json')
    return open(default_config_path, 'r').read()


def init(path):
    if path:
        os.chdir(path)

    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, 'config.json')

    if os.path.exists(config_path):
        print('These is a config.json in current directory(%s), '
              'Have you run `catsup init` before?' % current_dir)
        return

    posts_folder = prompt('posts folder', default='posts')

    deploy_folder = prompt('output folder', default='deploy')

    if not (posts_folder.startswith('.') or os.path.exists(posts_folder)):
        os.makedirs(posts_folder)

    template = get_template().replace('posts', posts_folder)
    template = template.replace('deploy', deploy_folder)

    with open(config_path, 'w') as f:
        f.write(template)

    print('catsup init success!')
    print('Plese edit the generated config.json to configure your blog. ')


def parse(path):
    """
    Parser json configuration file
    """
    try:
        f = open(path, 'r')
    except IOError:
        print("Can't find config file %s" % path)

        if prompt_bool("Create a new config file", default=True):
            init('')
        else:
            logger.error("Can't find config file."
                         "Exiting catsup.")
        sys.exit(0)
    return update_nested_dict(ObjectDict(), json_decode(f.read()))


def load(path=None, base_url=None):
    # Read default configuration file first.
    # So catsup can use the default value when user's conf is missing.
    # And user does't have to change conf file everytime he updates catsup.
    default_config = os.path.join(g.public_templates_path, 'config.json')
    config = parse(default_config)

    if path:
        user_config = parse(path)
        config = update_nested_dict(config, user_config)
        os.chdir(os.path.abspath(os.path.dirname(path)))
    g.theme = catsup.themes.find(config)
    g.source = config.config.source
    g.output = config.config.output
    g.permalink = config.permalink
    if base_url:
        g.base_url = add_slash(base_url)
    else:
        g.base_url = urljoin(
            add_slash(config.site.domain),
            add_slash(config.site.root_path)
        )
    g.static_prefix = urljoin(
        g.base_url,
        add_slash(config.config.static_prefix)
    )

    config.theme.vars = update_nested_dict(config.theme.vars, g.theme.vars)
    return config
