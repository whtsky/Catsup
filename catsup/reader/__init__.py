# -*- coding:utf-8 -*-

from .markdown import markdown_reader
from .txt import txt_reader
from .html import html_reader

READERS = dict()


def register_reader(ext, f):
    if isinstance(ext, (list, tuple)):
        for e in ext:
            READERS[e.lower()] = f
    else:
        READERS[ext.lower()] = f


def get_reader(ext):
    return READERS.get(ext, None)


register_reader(["md", "markdown"], markdown_reader)
register_reader("txt", txt_reader)
register_reader(["htm", "html"], html_reader)