import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

from nose.tools import raises


def test_config_parser():
    from catsup.parser.config import parse
    from catsup.utils import ObjectDict
    config = parse(os.path.join(BASE_DIR, "config.json"))
    assert config == ObjectDict({u'site': {u'url': u'http://blog.com/', u'name': u'blogname', u'description': u'Just another catsup blog'}, u'author': {u'twitter': u'twitter', u'name': u'nickname', u'email': u'name@exmaple.com'}})


@raises(SystemExit)
def test_parser_non_exist_file():
    from catsup.parser.config import parse
    parse("fd")
