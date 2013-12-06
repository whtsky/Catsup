from .markdown import markdown_reader

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
