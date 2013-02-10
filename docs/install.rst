.. _installation:

Installation
==============

Setuptools and Pip
-------------------
If you have pip installed ::

    (sudo) pip install catsup

Or if you don't have pip, try easy_install instead ::

    (sudo) easy_install catsup

Git
------
Install with git can always have the latest code ::

    git clone git://github.com/whtsky/catsup.git
    cd catsup

    # We use git submodules to organize out theme.
    # If you don't want the default theme(current version is sealscript)
    # You can skip these command.
    git submodule init
    git submodule update

    python setup.py install

Attention
---------------------
Catsup uses misaka as the markdown engine.It requires C compiler.On Ubuntu, you may run ::

    (sudo) apt-get install python-dev

If you're using a Mac, you need to install XCode and its Command Line Tools.

Windows User?
--------------
Sorry that I don't use Windows and I also don't know how to install it.That should works well with Cygwin.
If you're using Windows and know how to install catsup on Windows,
please fork this doc , add it and send a pull request.
