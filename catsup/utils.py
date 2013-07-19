import os
import sys
import subprocess

from urlparse import urljoin
from tornado.util import ObjectDict
from catsup.options import g

py = sys.version_info
py3k = py >= (3, 0, 0)

if py3k:
    basestring = str
    unicode = str


def static_url(file):
    import os
    import hashlib

    from catsup.logger import logger
    from catsup.options import g

    def get_hash(path):
        path = os.path.join(g.theme.path, 'static', path)
        if not os.path.exists(path):
            logger.warn("%s does not exist." % path)
            return ''

        with open(path, 'r') as f:
            return hashlib.md5(f.read()).hexdigest()[:4]

    hsh = get_hash(file)
    return urljoin(
        g.static_prefix,
        '%s?v=%s' % (file, hsh)
    )


def url_for(obj):
    from catsup.options import g
    from catsup.generator.models import CatsupPage

    url = ''
    if obj == 'index':
        url = g.base_url
    elif isinstance(obj, CatsupPage):
        url = obj.permalink
    elif isinstance(obj, str):
        url = g.permalink[obj]
    if url:
        return urljoin(
            g.base_url,
            url
        )


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
    for k, v in b.iteritems():
        if isinstance(v, dict):
            d = a.setdefault(k, ObjectDict())
            update_nested_dict(d, v)
        else:
            a[k] = v
    return a


def call(cmd, silence=False, **kwargs):
    if isinstance(cmd, str):
        cmd = cmd.split()
    if 'cwd' not in kwargs:
        kwargs['cwd'] = g.cwdpath
    if silence and 'stdout' not in kwargs:
        kwargs["stdout"] = subprocess.PIPE
    return subprocess.call(cmd, **kwargs)


def check_git():
    """
    Check if the environment has git installed
    :return: Bool. True for installed and False for not.
    """
    return call('git --help', silence=True) == 0


def check_rsync():
    """
    Check if the environment has rsynv installed
    :return: Bool. True for installed and False for not.
    """
    return call('rsync --help', silence=True) == 0


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def smart_copy(source, target):
    def copy_file(source, target):
        if os.path.exists(target):
            if os.path.getsize(source) == os.path.getsize(target):
                return
        open(target, "wb").write(open(source, "rb").read())

    if os.path.isfile(source):
        return copy_file(source, target)

    for f in os.listdir(source):
        sourcefile = os.path.join(source, f)
        targetfile = os.path.join(target, f)
        if os.path.isfile(sourcefile):
            smart_copy(sourcefile, targetfile)
        else:
            if not os.path.exists(targetfile):
                os.makedirs(targetfile)
            smart_copy(sourcefile, targetfile)
