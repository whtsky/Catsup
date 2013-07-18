from .config import load
from .markdown import md


def markdown(content, **kwargs):
    return md.render(content, **kwargs)


def config(path):
    return load(path)
