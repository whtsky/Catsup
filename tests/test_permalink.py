# -*- coding:utf-8 -*-

import os
import catsup.parser

from catsup.options import g
from catsup.reader import txt_reader

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def test_post_permalink():
    post_path = os.path.join(BASE_DIR, "post.txt")
    post = txt_reader(post_path)
    g.config = catsup.parser.config(os.path.join(BASE_DIR, "config.json"))
    g.config.permalink.post = "/{title}/"
    assert post.permalink == "/Hello,-World!/"
    g.config.permalink.post = "/{filename}/"
    assert post.permalink == "/post/"
    g.config.permalink.post = "/{date}/{title}/"
    assert post.permalink == "/2014-01-04/Hello,-World!/"
    g.config.permalink.post = "/{datetime.year}/{filename}/"
    assert post.permalink == "/2014/post/"