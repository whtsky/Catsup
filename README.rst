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

The ``category`` property defines the category of the post, but it's not used yet.

The ``date`` property can overwrite the date from the file name.

The ``tags`` property defines the tags of the post.

The ``comment`` property defines whether the post can be commented or not.

Post excerpt
-------------
You can use ``<!--more-->`` to define an excerpt of a post.

Any content before that will be used as excerpt of the post.

And you can choose to display excerpt rather than full content on your homepage.


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