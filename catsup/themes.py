#coding=utf-8
from __future__ import with_statement

import sys
import os
import logging

from tornado.util import ObjectDict
from catsup.options import config, g


def read_meta(path):
    """
    :param path: path for the theme.
    :return: Theme meta read in path.
    """
    if not os.path.exists(path):
        return
    meta = os.path.join(path, 'theme.py')
    if not os.path.exists(meta):
        logging.warn("%s is not a catsup theme." % path)
        return
    theme = ObjectDict(
        name='',
        author='',
        homepage='',
        pages=[],
        has_index=False,
        path=path,
        vars={},
    )
    execfile(meta, {}, theme)
    templates_path = os.path.join(path, 'templates')
    for page in theme.pages:
        if page == 'page.html':
            theme.has_index = True
            # If your theme does not have index page,
            # catsup will rename page/1.html to page.html.
        if not os.path.exists(os.path.join(templates_path, page)):
            logging.warning("%s announces a page %s"
                         " which not exists." % (theme.name, page))
    return theme


def find(theme_name=''):
    if not theme_name:
        theme_name = config.theme.name
    theme_gallery = [
        os.path.join(os.path.abspath('themes'), theme_name),
        os.path.join(g.catsup_path, 'themes', theme_name),
    ]
    for path in theme_gallery:
        theme = read_meta(path)
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
        for theme in names:
            themes.add(theme)
    print('Available themes: \n')
    for name in themes:
        theme = find(name)
        print('Name: %s' % theme.name)
        print('Author: %s' % theme.author)
        print('HomePage: %s' % theme.homepage)
        print('----')


def install():
    import shutil

    if len(sys.argv) < 2:
        print('Usage: catsup install path [-g]')
        sys.exit(0)

    themes_path = os.path.abspath('themes')
    if len(sys.argv) == 3 and sys.argv.pop(2) == '-g':
        themes_path = os.path.join(g.catsup_path, 'themes')

    path = sys.argv.pop(1)

    logging.info('Installing theme from %s' % path)

    if not os.path.exists(themes_path):
        os.makedirs(themes_path)

    if os.path.exists(path):
        meta = read_meta(path)
        if not meta:
            sys.exit(0)
        name = meta.name
        logging.info("Found theme %s" % name)

        install_path = os.path.join(themes_path, name)

        if not os.path.exists(install_path):
            os.makedirs(install_path)

        shutil.copytree(path, install_path)
    elif path.lower().endswith('.git'):  # a git repo
        os.chdir(themes_path)
        os.system('git clone %s' % path)
        repo_folder = path.split('/')[-1][:-4]
        meta = read_meta(repo_folder)
        if not meta:
            shutil.rmtree(repo_folder)
            sys.exit(0)
        name = meta.name
        os.rename(repo_folder, meta.name)

    else:
        logging.error("Can't install theme from %s." % path)
        sys.exit(0)

    logging.info('Theme %s successfully installed' % name)
