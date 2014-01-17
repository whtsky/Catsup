import os
import shutil
import tempfile

from catsup.logger import logger
from catsup.parser.themes import find_theme, read_theme
from catsup.utils import call, mkdir
from catsup.themes.utils import search_github

THEMES_PATH = os.path.abspath("themes")


def install_from_git(clone_url):
    mkdir(THEMES_PATH)
    os.chdir(THEMES_PATH)
    tmp_dir = tempfile.mkdtemp()
    os.system('git clone {clone_url} {tmp_dir}'.format(
        clone_url=clone_url,
        tmp_dir=tmp_dir
    ))
    theme = read_theme(tmp_dir)
    if not theme:
        logger.error("{clone_url} is not a Catsup theme repo.".format(
            clone_url=clone_url
        ))
        shutil.rmtree(tmp_dir)
    if os.path.exists(theme.name):
        shutil.rmtree(theme.name)

    os.rename(tmp_dir, theme.name)
    logger.info("Installed theme {name}".format(name=name))


def search_and_install(name):
    logger.info("Searching theme {name} on GitHub..".format(name=name))
    item = search_github(name=name)
    if not item:
        logger.error("Can't find theme {name}.".format(name=name))
        exit(1)

    logger.info("Fount {name} on GitHub.".format(name=item["name"]))
    install_from_git(item["clone_url"])


def install_theme(name):
    theme = find_theme(theme_name=name, silence=True)
    if theme:
        # Update theme
        if not os.path.exists(os.path.join(theme.path, '.git')):
            logger.warn("%s is not installed via git."
                        "Can't update it." % theme.name)
        else:
            logger.info("Updating theme %s" % theme.name)
            call("git pull", cwd=theme.path)
        exit(0)

    if ".git" in name or "//" in name:
        install_from_git(name)
    else:
        search_github(name)
