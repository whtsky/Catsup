import os
import re
import sys
import subprocess

try:
    from urllib.parse import urljoin
    assert urljoin
except ImportError:
    from urlparse import urljoin

from tornado.util import ObjectDict

py = sys.version_info
py3k = py >= (3, 0, 0)

if py3k:
    basestring = str
    unicode = str


HTML_TAG_RE = re.compile("<.*?>")


def html_to_raw_text(html):
    return "".join(HTML_TAG_RE.split(html))


def static_url(f):
    from catsup.options import g
    caches_class = g.generator.caches["static_url"]
    if f not in caches_class:
        import os
        import hashlib

        from catsup.logger import logger

        def get_hash(path):
            path = os.path.join(g.theme.path, 'static', path)
            if not os.path.exists(path):
                logger.warn("%s does not exist." % path)
                return

            with open(path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()

        hsh = get_hash(f)
        url = urljoin(
            g.static_prefix,
            '%s?v=%s' % (f, hsh)
        )
        caches_class[f] = url
    return caches_class[f]


def url_for(obj):
    from catsup.options import g
    caches_class = g.generator.caches["url_for"]
    key = id(obj)
    if key not in caches_class:
        from catsup.generator.models import CatsupPage

        url = ''
        if obj == 'index':
            url = g.base_url
        elif isinstance(obj, CatsupPage):
            url = obj.permalink
        elif isinstance(obj, str):
            url = g.permalink[obj]
        caches_class[key] = urljoin(
            g.base_url,
            url
        )
    return caches_class[key]


def to_unicode(value):
    if isinstance(value, unicode):
        return value
    if isinstance(value, basestring):
        return value.decode('utf-8')
    if isinstance(value, int):
        return str(value)
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value


def update_nested_dict(a, b):
    for k, v in b.items():
        if isinstance(v, dict):
            d = a.setdefault(k, ObjectDict())
            update_nested_dict(d, v)
        else:
            a[k] = v
    return a


def call(cmd, silence=False, **kwargs):
    from catsup.options import g
    if 'cwd' not in kwargs:
        kwargs['cwd'] = g.cwdpath
    if silence and 'stdout' not in kwargs:
        kwargs["stdout"] = subprocess.PIPE
    kwargs.setdefault("shell", True)
    return subprocess.call(cmd, **kwargs)


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def smart_copy(source, target):
    if not os.path.exists(source):
        return

    def copy_file(source, target):
        if os.path.exists(target):
            if os.path.getsize(source) == os.path.getsize(target):
                return
        mkdir(os.path.dirname(target))
        open(target, "wb").write(open(source, "rb").read())

    if os.path.isfile(source):
        return copy_file(source, target)

    for f in os.listdir(source):
        sourcefile = os.path.join(source, f)
        targetfile = os.path.join(target, f)
        if os.path.isfile(sourcefile):
            copy_file(sourcefile, targetfile)
        else:
            smart_copy(sourcefile, targetfile)
