import sys

import os
from tornado.util import ObjectDict
from tornado.escape import json_decode
from parguments.cli import prompt_bool
from catsup.logger import logger
from catsup.options import g
from catsup.utils import update_nested_dict, urljoin
from .utils import add_slash, create_config_file
import catsup.parser.themes


def parse(path):
    """
    Parser json configuration file
    """
    try:
        f = open(path, 'r')
    except IOError:
        print("Can't find config file %s" % path)

        if prompt_bool("Create a new config file", default=True):
            create_config_file()
        else:
            logger.error("Can't find config file. Exiting..")
        sys.exit(0)
    return update_nested_dict(ObjectDict(), json_decode(f.read()))


def load(path=None, local=False, base_url=None):
    # Read default configuration file first.
    # So catsup can use the default value when user's conf is missing.
    # And user does't have to change conf file everytime he updates catsup.
    default_config = os.path.join(g.public_templates_path, 'config.json')
    config = parse(default_config)

    if path:
        user_config = parse(path)
        config = update_nested_dict(config, user_config)
        os.chdir(os.path.abspath(os.path.dirname(path)))
    g.theme = catsup.parser.themes.find(config)
    g.source = config.config.source
    g.output = config.config.output
    g.permalink = config.permalink
    if base_url:
        g.base_url = add_slash(base_url)
    else:
        g.base_url = add_slash(config.site.url)
    config.site.url = g.base_url
    if local:
        import tempfile
        config.config.static_prefix = "/static/"
        config.config.output = tempfile.mkdtemp()

    g.static_prefix = urljoin(
        g.base_url,
        add_slash(config.config.static_prefix)
    )

    g.theme.vars = update_nested_dict(g.theme.vars, config.theme.vars)
    config.theme.vars = g.theme.vars
    config.path = path
    return config
