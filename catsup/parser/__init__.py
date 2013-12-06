from .config import load


def config(*args, **kwargs):
    return load(*args, **kwargs)
