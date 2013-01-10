#!/usr/bin/env python
#coding=utf-8

import sys
import os
import copy
import tornado
from tornado.options import options

try:
    import catsup
    print('Starting catsup version: %s' % catsup.__version__)
except ImportError:
    import site
    site_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    site.addsitedir(site_dir)

from catsup import config
config.init()

from catsup.tools import catsup_init, catsup_build, catsup_server
from catsup.tools import catsup_list_themes, catsup_install_theme
from catsup.tools import catsup_webhook, catsup_config

if len(sys.argv) > 1:
    _args = copy.deepcopy(sys.argv)
    _args.pop(1)
    tornado.options.parse_command_line(_args)

# Loading user settings
config.parse_config_file(options.settings)


def main():
    try:
        args = sys.argv
        if len(args) < 2:
            print('Useage: catsup server/build/webhook')
            sys.exit(0)
        cmd = args.pop(1)
        if cmd == 'server':
            catsup_server()
        elif cmd == 'build':
            catsup_build()
        elif cmd == 'webhook':
            catsup_webhook()
        elif cmd == 'init':
            # init catsup
            catsup_init()
        elif cmd == 'config':
            # generate config
            catsup_config();
        elif cmd == 'themes':
            # list available themes
            catsup_list_themes()
        elif cmd == 'install':
            # install a new theme
            catsup_install_theme()
        else:
            print('Unknow Command: %s' % cmd)
            sys.exit(0)
    except (EOFError, KeyboardInterrupt):
        print('\nExiting catsup...')
        sys.exit(0)

# this is for testing catsup without install it
if __name__ == '__main__':
    main()
