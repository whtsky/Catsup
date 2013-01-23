#coding=utf-8
from __future__ import with_statement

import os

from catsup.options import g
from catsup.utils import find_theme


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
        for theme in names:
            themes.add(theme)
    print('Available themes: \n')
    for name in themes:
        theme = find_theme(name)
        print('Name: %s' % theme.name)
        print('Author: %s' % theme.author)
        print('HomePage: %s' % theme.homepage)
        print('----')


def install():
    pass
