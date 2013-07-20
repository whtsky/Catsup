#coding=utf-8
from __future__ import with_statement

import sys
import os
import shutil

from tornado.util import ObjectDict
from catsup.logger import logger
from catsup.options import g
from catsup.utils import call


def read_meta(path):
    """
    :param path: path for the theme.
    :return: Theme meta read in path.
    """
    if not os.path.exists(path):
        return
    meta = os.path.join(path, 'theme.py')
    if not os.path.exists(meta):
        logger.warn("%s is not a catsup theme." % path)
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
            logger.warning("%s announces a page %s"
                           " which not exists." % (theme.name, page))
    theme.name = theme.name.lower()
    return theme


def find(theme_name=''):
    if not theme_name:
        theme_name = g.theme.name
    theme_name = theme_name.lower()
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
    themes_text = []
    for name in themes:
        theme = find(name)
        themes_text.append("\n".join([
            'Name: %s' % theme.name,
            'Author: %s' % theme.author,
            'HomePage: %s' % theme.homepage
        ]))
    print("\n--------\n".join(themes_text))


def install(path):
    try:
        theme = find(path)
    except Exception:
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
        meta = read_meta(path)
        if not meta:
            sys.exit(0)
        name = meta.name
        logger.info("Found theme %s" % name)

        install_path = os.path.join(themes_path, name)

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
        logger.error("Can't install theme from %s." % path)
        sys.exit(0)

    logger.info('Theme %s successfully installed' % name)
