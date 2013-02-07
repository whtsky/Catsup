================
catsup
================

.. image:: https://travis-ci.org/whtsky/catsup.png?branch=master
    :target: https://travis-ci.org/whtsky/catsup

A lightweight static blog generator.

Install
========

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
===============

Change directory to the directory you prefer to place your blog and run ``catsup init`` to initialize it.

Then you can edit ``config.json`` to change your configuration.


Write a post
============
catsup uses Markdown to write posts.
Filename should like ``year-month-day-title.md``

(For example: ``2000-01-01-catsup.md``)

Post Example::

    #Title

    ----

    Content
    ```python
    print "hi,I'm coding."
    ```

Post properties
================
catsup supports some post properties. Write them before ``---``
 and start with ``-`` .
Example::

    - category: A Category
    - date: 2012-12-24
    - tags: tag1, tag2
    - comment: disabled
    - summary: this is a simple post.

The ``category`` property defines the category of the post, but it's not used yet.

The ``date`` property can overwrite the date from the file name.

The ``tags`` property defines the tags of the post.

The ``comment`` property defines whether the post can be commented or not.

Post summary
-------------

You can choose to display summary rather than full content on your homepage
by changing `display_summary` in your configuration file.

If you defined summary as a post property, catsup will use it.

Otherwise, we will try to analytic the summary in order of:

1. Content before`<!--more-->` in your post.

2. Content before first horizontal rule(like `***`)

3. Content before second header(like '##xx')


Install theme
=============

Run ``catsup themes`` to list available themes. And run ``catsup install path [-g]`` to install a new theme.

If ``-g`` flag present, the theme would be install in the global themes directory.

``path`` could be a url of a git repo or path to the theme folder.

If it's a git repo, catsup will clone and install it automatically.


Build your blog
=================
run ``catsup build``
And you can find your static blog in ``~/build/`` .

Develop
==========
Catsup needs your code.Fork and code the repo, then run ::

    python setup.py develop

And start hacking catsup!
Note that all the code must be flask8 passed ::

    flake8 catsup