#!/usr/bin/env python
#coding=utf-8

import sys
major, minor = sys.version_info[:2]
if major < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os
from catsup.options import g, enable_pretty_logging

enable_pretty_logging()

g.catsup_path = os.path.abspath(os.path.dirname(__file__))
g.public_templates_path = os.path.join(g.catsup_path, 'templates')

try:
    import catsup
except ImportError:
    import site
    site.addsitedir(os.path.dirname(g.catsup_path))

doc = """catsup v%s

Usage:
    catsup init [<path>]
    catsup build [-s <file>|--settings=<file>]
    catsup server [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup webhook [-s <file>|--settings=<file>] [-p <port>|--port=<port>]
    catsup themes
    catsup install <theme> [-g|--global]
    catsup -h | --help
    catsup --version

Options:
    -h --help               show this screen.
    -s --settings=<file>    specify a config file. [default: config.json]
    -p --port=<port>        specify the server port. [default: 8888]
    -g --global             install theme to global theme folder.
""" % catsup.__version__



import catsup.config
import catsup.server
import catsup.themes
import catsup.build


from parguments import Parguments

parguments = Parguments(doc, version=catsup.__version__)

@parguments.command
def init(args):
    """
Usage:
    catsup init [<path>] [-s <file>|--settings=<file>]

Options:
    -h --help               show this screen.
    -s --settings=<file>    specify a setting file. [default: config.json]
    """
    catsup.config.init(args.get('<path>'))

@parguments.command
def build(args):
    """
Usage:
    catsup build [-s <file>|--settings=<file>]

Options:
    -h --help               show this screen.
    -s --settings=<file>    specify a setting file. [default: config.json]
    """
    path = args.get('--settings')
    catsup.config.load(path)
    catsup.build.build()


@parguments.command
def server(args):
    """
Usage:
    catsup server [-s <file>|--settings=<file>] [-p <port>|--port=<port>]

Options:
    -h --help               show this screen.
    -s --settings=<file>    specify a setting file. [default: config.json]
    -p --port=<port>        specify the server port. [default: 8888]
    """
    path = args.get('--settings')
    catsup.config.load(path)
    port = args.get('--port')
    catsup.server.preview(port=port)


@parguments.command
def webhook(args):
    """
Usage:
    catsup webhook [-s <file>|--settings=<file>] [-p <port>|--port=<port>]

Options:
    -h --help               show this screen.
    -s --settings=<file>    specify a setting file. [default: config.json]
    -p --port=<port>        specify the server port. [default: 8888]
    """
    path = args.get('--settings')
    catsup.config.load(path)
    port = args.get('--port')
    catsup.server.webhook(port=port)


@parguments.command
def themes(args):
    """
Usage:
    catsup themes

Options:
    -h --help               show this screen.
    """
    catsup.themes.list()


@parguments.command
def install(args):
    """
Usage:
    catsup install <theme> [-g|--global]

Options:
    -g --global             install theme to global theme folder.
    -h --help               show this screen.
    """
    g = args.get('--global')
    catsup.themes.install(g=g)

def main():
    parguments.run()


if __name__ == '__main__':
    main()
