# coding=utf-8
from __future__ import with_statement

import sys
import os
import shutil

from tornado.util import ObjectDict
from catsup.logger import logger
from catsup.options import g
from catsup.utils import call


def read_theme(path):
    """
    :param path: path for the theme.
    :return: Theme theme read in path.
    """
    if not os.path.exists(path):
        return
    theme_file = os.path.join(path, 'theme.py')
    if not os.path.exists(theme_file):
        logger.warn("%s is not a catsup theme." % path)
        return
    theme = ObjectDict(
        name='',
        author='',
        homepage='',
        path=path,
        post_per_page=5,
        vars={},
    )
    exec(open(theme_file).read(), {}, theme)
    theme.name = theme.name.lower()
    return theme


def find(config=None, theme_name=''):
    if not theme_name:
        theme_name = config.theme.name
    theme_name = theme_name.lower()
    theme_gallery = [
        os.path.join(os.path.abspath('themes'), theme_name),
        os.path.join(g.catsup_path, 'themes', theme_name),
    ]
    for path in theme_gallery:
        theme = read_theme(path)
        if theme:
            return theme

    raise Exception("Can't find theme: %s" % theme_name)


def list():
    theme_gallery = [
        os.path.abspath('themes'),
        os.path.join(g.catsup_path, 'themes'),
    ]
    themes = set()
    for path in theme_gallery:
        if not os.path.exists(path):
            continue
        names = os.listdir(path)
        for name in names:
            theme_path = os.path.join(path, name)
            if os.path.isdir(theme_path):
                themes.add(name)
    print('Available themes: \n')
    themes_text = []
    for name in themes:
        theme = find(theme_name=name)
        themes_text.append("\n".join([
            'Name: %s' % theme.name,
            'Author: %s' % theme.author,
            'HomePage: %s' % theme.homepage
        ]))
    print("\n--------\n".join(themes_text))


def install(path):
    try:
        theme = find(theme_name=path)
    except:
        pass
    else:
        # Update theme
        if not os.path.exists(os.path.join(theme.path, '.git')):
            logger.warn("%s is not installed via git."
                        "Can't update it." % theme.name)
        else:
            logger.info("Updating theme %s" % theme.name)
            call('git pull', cwd=theme.path)
        sys.exit(0)

    themes_path = os.path.abspath('themes')

    logger.info('Installing theme from %s' % path)

    if not os.path.exists(themes_path):
        os.makedirs(themes_path)

    if os.path.exists(path):
        theme = read_theme(path)
        if not theme:
            sys.exit(1)
        name = theme.name
        logger.info("Found theme %s" % name)

        install_path = os.path.join(themes_path, name)

        shutil.copytree(path, install_path)

    elif path.lower().endswith('.git'):  # a git repo
        os.chdir(themes_path)
        repo_folder = path.split('/')[-1][:-4]
        if os.path.exists(repo_folder):
            shutil.rmtree(repo_folder)
        os.system('git clone %s' % path)
        theme = read_theme(repo_folder)
        if not theme:
            shutil.rmtree(repo_folder)
            sys.exit(0)
        if os.path.exists(theme.name):
            shutil.rmtree(theme.name)

        os.rename(repo_folder, theme.name)

    else:
        logger.error("Can't install theme from %s." % path)
        sys.exit(1)

    logger.info('Theme %s successfully installed' % theme.name)
