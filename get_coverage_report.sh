#!/bin/sh

coverage run --source=catsup setup.py -q nosetests
if [ $? != 0 ]; then
    exit 1
fi
coverage html
open htmlcov/index.html