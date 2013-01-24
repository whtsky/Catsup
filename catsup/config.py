#coding=utf-8
from __future__ import with_statement
import os
import sys
from tornado.escape import json_decode
from tornado.options import options

from catsup.options import config, g
import catsup.themes


def init():

    if len(sys.argv) > 1:
        # Please note that sys.argv.pop(1) had been executed before here.
        # If length of sys.argv > 1, user runned command "catsup init xxx"
        # instead of "catsup init". And now sys.argv[1] == xxx,
        # we regard xxx as a directory relatively to current directory
        # to initialize catsup.
        os.chdir(sys.argv[1])

    current_dir = os.getcwd()
    config_path = os.path.join(current_dir, 'config.json')

    if os.path.exists(config_path):
        print('These is a config.json in current directory(%s), '
              'Have you run `catsup init` before?' % current_dir)
        return

    posts_folder = raw_input('posts folder:(posts by default)') or 'posts'

    deploy_folder = raw_input('output folder:(deploy by default)') or 'deploy'

    if not (posts_folder.startswith('.') or os.path.exists(posts_folder)):
        os.makedirs(posts_folder)

    default_config_path = os.path.join(g.public_templates_path, 'config.json')
    template = open(default_config_path, 'r').read()
    template = template.replace('posts', posts_folder)
    template = template.replace('deploy', deploy_folder)

    with open(config_path, 'w') as f:
        f.write(template)

    print('catsup init success!')
    print('Plese edit the generated config.json to configure your blog. ')


def parse():
    """
    Parser json configuration file
    """
    try:
        f = open(options.settings, 'r')
    except IOError:
        print("Can't find config file %s" % options.settings)
        _input = raw_input("Do you wish to create a new config file?(y/n)")
        if _input.lower() == 'y':
            init()
        else:
            import logging
            logging.error("Can't find config file."
                          "Exiting catsup.")
            sys.exit(0)
    else:
        config.update(json_decode(f.read()))
    os.chdir(os.path.abspath(os.path.dirname(options.settings)))


def load():
    parse()
    g.theme = catsup.themes.find()
