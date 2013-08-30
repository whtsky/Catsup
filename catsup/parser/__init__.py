from .config import load
from .markdown import md


def markdown(content, **kwargs):
    return md.render(content, **kwargs)


def config(*args, **kwargs):
    return load(*args, **kwargs)
