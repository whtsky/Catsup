catsup
----------------

.. image:: https://travis-ci.org/whtsky/catsup.png?branch-master
    :target: https://travis-ci.org/whtsky/catsup

A lightweight static blog generator.
Document here: https://catsup.readthedocs.org/en/latest/

Install
--------

Simple way using pip::

    pip install catsup


Or another hard way to install::

    git clone git://github.com/whtsky/catsup.git
    cd catsup

    # We use git submodules to organize out theme.
    # If you don't want the default theme(current version is sealscript)
    # You can skip these command.
    git submodule init
    git submodule update

    python setup.py install


Setup your blog
---------------

Change directory to the directory you prefer to place your blog and run ``catsup init`` to initialize it.

Then you can edit ``config.json`` to change your configuration.


Write a post
------------
Catsup support markup of Markdown.
Filename should like ``year-month-day-title.md``

(For example: ``2000-01-01-catsup.md``)

Post Example::

    #Title

    ----

    Content
    ```python
    print "hi,I'm coding."
    ```

Install theme
-------------

Run ``catsup themes`` to list available themes. And run ``catsup install path [-g]`` to install a new theme.

If ``-g`` flag present, the theme would be install in the global themes directory.

``path`` could be a url of a git repo or path to the theme folder.

If it's a git repo, catsup will clone and install it automatically.


Build your blog
-----------------
run ``catsup build``
And you can find your static blog in ``~/build/`` .