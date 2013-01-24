#!/usr/bin/env python
#coding=utf-8

import sys
major, minor = sys.version_info[:2]
if major < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import os
import copy
import logging
import tornado
from catsup.options import g

g.catsup_path = os.path.abspath(os.path.dirname(__file__))
g.public_templates_path = os.path.join(g.catsup_path, 'templates')

try:
    import catsup
except ImportError:
    import site
    site.addsitedir(os.path.dirname(g.catsup_path))

import catsup.config
import catsup.server
import catsup.themes
from catsup.build import build

from tornado.options import define

define("port", type=int, default=8888, help="run on the given port")
define('settings', type=str, default='config.json', help='config path')

if len(sys.argv) > 1:
    _args = copy.deepcopy(sys.argv)
    _args.pop(1)
    tornado.options.parse_command_line(_args)


def print_useage():
    print("""
Usage: catsup [command] [options]
command:
    help          print this page.
    version       print catsup version
    init          initialize catsup in current working directory.
    server        start a preview server.
    build         build the site, generate posts to deploy.
    webhook       start a webhook server.
    themes        list all available themes.
    install       install a theme

options:
    -g            with install command, to install a theme in global.
""")


def main():
    try:
        args = sys.argv
        if len(args) < 2:
            print_useage()
            sys.exit(0)
        cmd = args.pop(1)
        if cmd == 'init':
            catsup.config.init()
            sys.exit(0)
        elif cmd == 'version':
            print('catsup v%s' % catsup.__version__)
            sys.exit(0)
        elif cmd == 'themes':
            catsup.themes.list()
            sys.exit(0)
        elif cmd == 'install':
            catsup.themes.install()
            sys.exit(0)
        elif cmd == 'help':
            print_useage()
            sys.exit(0)

        catsup.config.load()
        if cmd == 'build':
            build()
        elif cmd == 'server':
            catsup.server.preview()
        elif cmd == 'webhook':
            catsup.server.webhook()
        else:
            print('Unknow Command: %s' % cmd)
            sys.exit(0)
    except (EOFError, KeyboardInterrupt):
        logging.info('\nExiting catsup...')
        sys.exit(0)


if __name__ == '__main__':
    main()
