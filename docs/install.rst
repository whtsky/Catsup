.. _installation:

Installation
==============


If you are familiar with Python, it is strongly suggested that you install everything in virtualenv.

If you are using OS X , make sure you have installed the *Command Line Tools* .

Install using pip
-------------------------
Install Catsup via pip is easy ::

    (sudo) pip install catsup


Upgrade from older version
-------------------------------
It's also easy to upgrade your Catsup ::

    (sudo) pip install catsup --upgrade

Install with Git
-----------------
Install with git can always have the latest code ::

    git clone git://github.com/whtsky/catsup.git
    cd catsup

    # We use git submodules to organize out theme.
    # If you don't want the default theme(current version is sealscript)
    # You can skip these command.
    git submodule init
    git submodule update

    python setup.py install

Cann’t find Python.h ?
-----------------------
Catsup uses misaka as the markdown engine. It requires C compiler.On Ubuntu, you may run ::

    (sudo) apt-get install python-dev

