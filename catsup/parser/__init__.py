import os
import hashlib
import marshal

from catsup.options import g

from .config import load
from .markdown import md


def markdown(content, **kwargs):
    hsh = hashlib.md5(content[:500]).hexdigest()
    cache_dir = os.path.join(g.cwdpath, ".catsup-cache")
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    cache_file = os.path.join(cache_dir, hsh)
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            cache = marshal.load(f)
        if cache["size"] == len(content):
            return cache["html"]
    html = md.render(content, **kwargs)
    cache = {
        "size": len(content),
        "html": html
    }
    with open(cache_file, "wb") as f:
        marshal.dump(cache, f)
    return html


def config(*args, **kwargs):
    return load(*args, **kwargs)
