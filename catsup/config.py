#coding=utf-8
from __future__ import with_statement
import os
import sys
from tornado.escape import json_decode
from tornado.options import options
from tornado.util import ObjectDict

from catsup.options import config, g
import catsup.themes


def init(path):

    if path:
        os.chdir(path)

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


def update_config(base, update):
    for key in update:
        if isinstance(update[key], dict):
            if key in base:
                update_config(base[key], update[key])
            else:
                # convert dict into ObjectDict.
                base[key] = ObjectDict(**update[key])
        else:
            base[key] = update[key]



def parse(path):
    """
    Parser json configuration file
    """
    try:
        f = open(path, 'r')
    except IOError:
        print("Can't find config file %s" % path)
        _input = raw_input("Do you wish to create a new config file?(y/n)")
        if _input.lower() == 'y':
            init('')
        else:
            import logging
            logging.error("Can't find config file."
                          "Exiting catsup.")
            sys.exit(0)
    else:
        update_config(config, json_decode(f.read()))


def load(path):
    # Read default configuration file first.
    # So catsup can use the default value when user's conf is missing.
    # And user does't have to change conf file everytime he updates catsup.
    parse(os.path.join(g.public_templates_path, 'config.json'))
    parse(path)
    os.chdir(os.path.abspath(os.path.dirname(path)))
    g.theme = catsup.themes.find()
    #  It's dirty now.Can it be better?
    update_config(g.theme.vars, config.theme.vars)
    update_config(config.theme.vars, g.theme.vars)