import sys
import os
import logging

major = sys.version_info[0]
if major < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from catsup.options import config, g, enable_pretty_logging

enable_pretty_logging()

g.catsup_path = os.path.abspath(os.path.dirname(__file__))
g.public_templates_path = os.path.join(g.catsup_path, 'templates')
g.cwdpath = os.path.abspath('.')

try:
    import catsup
except ImportError:
    import site
    site.addsitedir(os.path.dirname(g.catsup_path))

doc = """catsup v%s

Usage:
    catsup init [<path>]
    catsup build [-s <file>|--settings=<file>]
    catsup deploy [-s <file>|--settings=<file>]
    catsup git [-s <file>|--settings=<file>]
    catsup rsync [-s <file>|--settings=<file>]
    catsup server [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup webhook [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup themes
    catsup install <theme> [-g|--global]
    catsup migrate --wordpress -f <file>|--file=<file> [-o <dir>|--output=<dir>]
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

import catsup.config
import catsup.server
import catsup.themes
import catsup.build
import catsup.deploy
import catsup.migrate


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
    catsup.config.init(path)


@parguments.command
def build(settings):
    """
    Usage:
        catsup build [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    catsup.config.load(settings)
    catsup.build.build()


@parguments.command
def deploy(settings):
    """
    Usage:
        catsup deploy [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    catsup.config.load(settings)
    if config.deploy.default == 'git':
        catsup.deploy.git()
    elif config.deploy.default == 'rsync':
        catsup.deploy.rsync()
    else:
        logging.error("Unknown deploy: %s" % config.deploy.default)


@parguments.command
def git(settings):
    """
    Usage:
        catsup git [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    catsup.config.load(settings)
    catsup.deploy.git()


@parguments.command
def rsync(settings):
    """
    Usage:
        catsup rsync [-s <file>|--settings=<file>]

    Options:
        -h --help               Show this screen and exit.
        -s --settings=<file>    specify a setting file. [default: config.json]
    """
    catsup.config.load(settings)
    catsup.deploy.rsync()


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
    catsup.config.load(settings)
    catsup.server.preview(port=port)


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
    catsup.config.load(settings)
    catsup.server.webhook(port=port)


@parguments.command
def themes():
    """
    Usage:
        catsup themes

    Options:
        -h --help               Show this screen and exit.
    """
    catsup.themes.list()


@parguments.command
def install(theme, g):
    """
    Usage:
        catsup install <theme> [-g|--global]

    Options:
        -g --global             install theme to global theme folder.
        -h --help               Show this screen and exit.
    """
    catsup.themes.install(path=theme, g=g)


@parguments.command
def migrate(wordpress, file, output):
    """
    Usage:
        catsup migrate --wordpress -f <file>|--file=<file> [-o <dir>|--output=<dir>]

    Options:
        -h --help               Show this screen and exit.
        -f --file=<file>        specify a wordpress output file.
        -o --output=<dir>       specify a output folder. [default: .]
    """
    if wordpress:
        catsup.migrate.wordpress(file, output)


def main():
    parguments.run()

if __name__ == '__main__':
    main()
