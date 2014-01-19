import os
import ujson

from catsup.logger import logger
from catsup.options import g
from catsup.utils import update_nested_dict, urljoin, ObjectDict
from catsup.parser.themes import find_theme

from .utils import add_slash


def parse(path):
    """
    Parser json configuration file
    """
    try:
        f = open(path, 'r')
    except IOError:
        logger.error("Can't find config file."
                     "Run `catsup init` to generate a new config file.")
        exit(1)
    return update_nested_dict(ObjectDict(), ujson.load(f))


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
    g.theme = find_theme(config)
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
