#!/bin/sh

case $1 in
    server) python -m catsup.app server;;
    build) python -m catsup.app build;;
    webhook) python -m catsup.app webhook;;
    upload) python setup.py sdist bdist_egg upload;;
    *) echo "Usage: catsup <server | build | webhook>";;
esac
