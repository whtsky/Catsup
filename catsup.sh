#!/bin/sh

case $1 in
    server) python -m catsup.app server;;
    deploy) python -m catsup.app deploy;;
    webhook) python -m catsup.app webhook;;
    *) echo "Usage: catsup <server | deploy | webhook>";;
esac
