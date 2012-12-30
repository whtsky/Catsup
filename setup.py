#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='catsup',
    version='0.0.4',
    author='whtsky, messense',
    author_email='whtsky@me.com, wapdevelop@gmail.com',
    url='https://github.com/whtsky/catsup',
    packages=find_packages(),
    description='Catsup: a lightweight static blog generator',
    entry_points={
        'console_scripts': ['catsup= catsup.app:main'],
        },
    install_requires=[
        'tornado',
        'misaka',
        'pygments',
    ],
    include_package_data=True,
    license='MIT License',
)