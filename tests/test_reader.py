#coding: utf-8

import os

from nose.tools import raises
from catsup.utils import to_unicode

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def test_reader_choser():
    from catsup.reader import get_reader, markdown_reader, txt_reader
    assert get_reader("md") == markdown_reader
    assert get_reader("markdown") == markdown_reader
    assert get_reader("txt") == txt_reader


@raises(SystemExit)
def test_open_unexist_file():
    from catsup.reader.utils import open_file
    open_file(">_<")


def test_txt_reader():
    import datetime
    from catsup.reader import txt_reader
    post_path = os.path.join(BASE_DIR, "post.txt")
    post = txt_reader(post_path)
    assert post.path == post_path
    assert post.date == "2014-01-04"
    assert post.datetime == datetime.datetime(2014, 1, 4, 20, 56)
    assert post.title == "Hello, World!"
    assert post.content == to_unicode("<br />Hi!<br />I&#39;m happy to use Catsup!<br />中文测试<br />")


def test_read_txt_without_meta():
    from catsup.reader import txt_reader
    post_path = os.path.join(BASE_DIR, "no_meta.txt")
    post = txt_reader(post_path)
    assert post.title == "no_meta", post.title


def test_md_reader():
    from catsup.reader import markdown_reader
    post_path = os.path.join(BASE_DIR, "2013-02-11-test.md")
    post = markdown_reader(post_path)
    assert post.path == post_path