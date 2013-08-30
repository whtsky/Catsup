.. _configuration:

Configuration
===============

Catsup's configuration file is a vaild JSON file.

Overview
------------

The default config file looks like :

.. literalinclude:: config.json
    :language: json


Site & Author & Config
------------------------

It’s easy enough to configure these by yourself.

If you're using Google Analytics, remember to change ``config.analytics`` ::

    "config": {
            "source": "posts",
            "output": "deploy",
            "static_prefix": "/static/",
            "analytics": "UA-33275966-1"
    },


Permalink
-------------

You can easily change any page's permalink in ``config.permalink`` .

There are some permalink styles for posts you may like :

+ ``/{title}.html``
+ ``{filename}.html``
+ ``/{date}/{title}/``
+ ``/{filename}/``
+ ``/{date}/{filename}/``
+ ``/{datetime.year/{filename}/``

Note that permalink defined in :ref:`Post Meta <post-meta>` will be used first.

For example,  you defined your post permalink like ::

    "permalink": {
        "post": "/{title}/",
        "feed": "/feed.xml"
    },

And in your post, you defined a permalink in :ref:`Post Meta <post-meta>` ::

    # About

    - datetime: 2013-08-30 12:00
    - type: page
    - permalink: /about-the-site

    -------

    This is a about page

In the end the permalink of this page will be ``/about-the-site`` .

Comment
----------

Catsup supports two comment systems: `Disqus <http://disqus.com>`_ and `Duoshuo <http://duoshuo.com>`_

If you prefer Duoshuo to Disqus, just change your comment system to it ::

    "comment": {
        "allow": true,
        "system": "duoshuo",
        "shortname": "catsup"
    },

If you have your own shortname, remember to change ``comment.shortname`` to your own ::

    "comment": {
        "allow": true,
        "system": "disqus",
        "shortname": "my_site"
    },

If you don't want to allow any comment, just disable it ::

    "comment": {
        "allow": false
    },

If you just want some of the posts can't be commented, set ``- comment: disabled`` in :ref:`Post Meta <post-meta>`

Deploy & Theme
----------------

It’s easy enough to configure these by yourself.

For more information, read about :ref:`Deploy Support <deploy>` and your theme's document.