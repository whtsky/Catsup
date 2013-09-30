import os

from jinja2 import BytecodeCache
from catsup.options import g


def get_cache_path(name):
    """
    Return the cache file path to the given name.
    """
    return os.path.join(
        g.cwdpath,
        ".catsup-cache",
        name
    )


class CatsupJinjaCache(BytecodeCache):
    def __init__(self):
        self.directory = get_cache_path("jinja2")
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def load_bytecode(self, bucket):
        filename = os.path.join(self.directory, bucket.key)
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                bucket.load_bytecode(f)

    def dump_bytecode(self, bucket):
        filename = os.path.join(self.directory, bucket.key)
        with open(filename, 'wb') as f:
            bucket.write_bytecode(f)


bytecode_cache = CatsupJinjaCache()