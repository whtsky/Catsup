#!/usr/bin/env python
#coding=utf-8

import sys
kwargs = {}
major, minor = sys.version_info[:2]
if major >= 3:
    kwargs['use_2to3'] = True

from setuptools import setup, find_packages

import catsup

setup(
    name='catsup',
    version=catsup.__version__,
    author='whtsky, messense',
    author_email='whtsky@me.com, wapdevelop@gmail.com',
    url='https://github.com/whtsky/catsup',
    packages=find_packages(),
    description='Catsup: a lightweight static blog generator',
    long_description=open('README.rst').read(),
    entry_points={
        'console_scripts': ['catsup= catsup.app:main'],
    },
    install_requires=[
        'tornado',
        'misaka',
        'pygments',
        'jinja2'
    ],
    include_package_data=True,
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
#        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
    ],
    **kwargs
)
