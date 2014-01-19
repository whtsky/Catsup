import sys
import os

major = sys.version_info[0]
if major < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from catsup.options import g
from catsup.logger import logger, enable_pretty_logging

enable_pretty_logging()

g.catsup_path = os.path.abspath(os.path.dirname(__file__))
g.public_templates_path = os.path.join(g.catsup_path, 'templates')
g.cwdpath = os.path.abspath('.')

import catsup

doc = """Catsup v%s

Usage:
    catsup init [<path>]
    catsup build [-s <file>|--settings=<file>]
    catsup deploy [-s <file>|--settings=<file>]
    catsup git [-s <file>|--settings=<file>]
    catsup rsync [-s <file>|--settings=<file>]
    catsup server [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup webhook [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup watch [-s <file>|--settings=<file>]
    catsup clean [-s <file>|--settings=<file>]
    catsup themes
    catsup install <theme>
    catsup -h | --help
    catsup --version

Options:
    -h --help               Show this screen and exit.
    -s --settings=<file>    specify a config file. [default: config.json]
    -f --file=<file>        specify a wordpress output file.
    -o --output=<dir>       specify a output folder. [default: .]
    -p --port=<port>        specify the server port. [default: 8888]
    -g --global             install theme to global theme folder.
""" % catsup.__version__

from parguments import Parguments

parguments = Parguments(doc, version=catsup.__version__)


@parguments.command
def init(path):
    """
    Usage:
        catsup init [<path>]

    Options:
        -h --help               Show this screen and exit.
    """
    from catsup.parser.utils import create_config_file
    create_config_file(path)


@parguments.command
def build(settings):
    """
    Usage:
        catsup build [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    from catsup.generator import Generator
    generator = Generator(settings)
    generator.generate()


@parguments.command
def deploy(settings):
    """
    Usage:
        catsup deploy [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    import catsup.parser
    import catsup.deploy
    config = catsup.parser.config(settings)
    if config.deploy.default == 'git':
        catsup.deploy.git(config)
    elif config.deploy.default == 'rsync':
        catsup.deploy.rsync(config)
    else:
        logger.error("Unknown deploy: %s" % config.deploy.default)


@parguments.command
def git(settings):
    """
    Usage:
        catsup git [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    import catsup.parser.config
    import catsup.deploy
    config = catsup.parser.config(settings)
    catsup.deploy.git(config)


@parguments.command
def rsync(settings):
    """
    Usage:
        catsup rsync [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    import catsup.parser.config
    import catsup.deploy
    config = catsup.parser.config(settings)
    catsup.deploy.rsync(config)


@parguments.command
def server(settings, port):
    """
    Usage:
        catsup server [-s <file>|--settings=<file>] [-p <port>|--port=<port>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
        -p --port=<port>        specify the server port. [default: 8888]
    """
    import catsup.server
    preview_server = catsup.server.PreviewServer(settings, port)
    preview_server.run()


@parguments.command
def webhook(settings, port):
    """
    Usage:
        catsup webhook [-s <file>|--settings=<file>] [-p <port>|--port=<port>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
        -p --port=<port>        specify the server port. [default: 8888]
    """
    import catsup.server
    server = catsup.server.WebhookServer(settings, port)
    server.run()


@parguments.command
def watch(settings):
    """
    Usage:
        catsup watch [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    from catsup.generator import Generator
    from catsup.server import CatsupEventHandler
    from watchdog.observers import Observer

    generator = Generator(settings)
    generator.generate()
    event_handler = CatsupEventHandler(generator)
    observer = Observer()
    for path in [generator.config.config.source, g.theme.path]:
        path = os.path.abspath(path)
        observer.schedule(event_handler, path=path, recursive=True)
    observer.start()
    while True:
        pass


@parguments.command
def clean(settings):
    """
    Usage:
        catsup clean [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    import shutil
    import catsup.parser.config
    config = catsup.parser.config(settings)

    for path in [config.config.static_output, config.config.output]:
        if os.path.exists(path):
            shutil.rmtree(path)


@parguments.command
def themes():
    """
    Usage:
        catsup themes

    Options:
        -h --help               Show this screen and exit.
    """
    from catsup.parser.themes import list_themes
    list_themes()


@parguments.command
def install(name):
    """
    Usage:
        catsup install <name>

    Options:
        -h --help               Show this screen and exit.
    """
    from catsup.themes.install import install_theme
    install_theme(name=name)


def main():
    parguments.run()
