#coding: utf-8

from houdini import escape_html

from catsup.utils import to_unicode
from catsup.reader.html import html_reader


def txt_reader(path):
    post = html_reader(path)
    content = post.content.encode("utf-8")
    content = escape_html(content)
    content = content.replace(
        "\n",
        "<br />"
    )
    post.content = to_unicode(content)
    return post
