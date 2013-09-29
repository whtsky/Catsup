from .config import load
from .markdown import md


def markdown(content, **kwargs):
    html = md.render(content, **kwargs)
    return html


def config(*args, **kwargs):
    return load(*args, **kwargs)
