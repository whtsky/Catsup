import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SITE_DIR = os.path.join(BASE_DIR, "site")

os.chdir(SITE_DIR)

from nose.tools import raises
from catsup.options import g
g.cwdpath = SITE_DIR


def output_exist(path):
    return os.path.exists(os.path.join(
        SITE_DIR,
        "deploy",
        path
    ))


def test_build():
    from catsup.cli import clean, build
    clean(settings="config.json")
    build(settings="config.json")
    assert output_exist("feed.xml")
    assert output_exist("index.html")
    assert output_exist("page.html")
    assert output_exist("sitemap.txt")
    assert output_exist("should-exist")
    assert not output_exist(".should-not-exist")


def test_init():
    from catsup.cli import init
    os.remove("config.json")
    init("./")


@raises(SystemExit)
def test_reinit():
    from catsup.cli import init
    init("./")


def test_generate_without_post():
    from catsup.cli import clean, build
    clean(settings="config2.json")
    build(settings="config2.json")
    assert not output_exist("page.html")
