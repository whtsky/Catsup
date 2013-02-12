import os

CWD = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'blog')

import catsup.utils


def call(cmd):
    assert catsup.utils.call(cmd, silence=True, cwd=CWD) == 0


def test():
    call('catsup build')
    call('catsup themes')
    call('catsup install git://github.com/whtsky/catsup-theme-sealscript.git')
    call('catsup install sealscript')
    call('catsup -h')
    call('catsup --version')
    call('rm -rf themes')
