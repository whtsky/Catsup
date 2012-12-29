#!/bin/sh

case $1 in
    server) python -m catsup.app server;;
    deploy) python -m catsup.app deploy;;
    webhook) python -m catsup.app webhook;;
    upload) python setup.py sdist bdist_egg upload;;
    *) echo "Usage: catsup <server | deploy | webhook>";;
esac
