#coding=utf-8
from __future__ import with_statement
import os
import sys
from tornado.escape import json_decode
from catsup.options import config, g
from catsup.utils import find_theme

from tornado.options import options

def init():

    if len(sys.argv) > 1:
        # Please note that sys.argv.pop(1) had been executed before here.
        # If length of sys.argv > 1, user runned command "catsup init xxx"
        # instead of "catsup init". And now sys.argv[1] == xxx,
        # we regard xxx as a directory relatively to current directory
        # to initialize catsup.
        os.chdir(sys.argv[1])

    catsup_dir = os.getcwd()
    config_path = os.path.join(catsup_dir, 'config.json')

    if os.path.exists(config_path):
        print('These is a config.json in current directory(%s), '
              'plese check whether you have set up catsup before.' % catsup_dir)
        return


    posts_folder = raw_input('posts folder:(posts by default)') or 'posts'

    deploy_folder = raw_input('output folder:(deploy by default)') or 'deploy'

    if not (posts_folder.startswith('.') or os.path.exists(posts_folder)):
        os.makedirs(posts_folder)

    default_config_path = os.path.join(g.public_templates_path, 'config.json')
    config = open(default_config_path, 'r').read()
    config = config.replace('posts', posts_folder)
    config = config.replace('deploy', deploy_folder)

    with open(config_path, 'w') as f:
        f.write(config)

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
        config.update(json_decode(f.read()))


def load():
    parse()
    g.theme = find_theme()
