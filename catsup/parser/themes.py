# coding=utf-8
from __future__ import with_statement

import sys
import os

from catsup.logger import logger
from catsup.options import g
from catsup.utils import call, ObjectDict


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


def find_theme(config=None, theme_name='', silence=False):
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

    if not silence:
        logger.error("Can't find theme: {name}".format(name=theme_name))
        exit(1)


def list_themes():
    theme_gallery = [
        os.path.abspath('themes'),
        os.path.join(g.catsup_path, 'themes'),
    ]
    themes = ()
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
