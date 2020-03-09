import os
import pytest

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SITE_DIR = os.path.join(BASE_DIR, "site")


@pytest.fixture
def site_dir():
    return SITE_DIR


@pytest.fixture
def output_exist():
    return lambda path: os.path.exists(os.path.join(SITE_DIR, "deploy", path))


@pytest.fixture(autouse=True)
def chdir():
    from catsup.options import g

    os.chdir(SITE_DIR)
    g.cwdpath = SITE_DIR
