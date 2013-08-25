.. _get-started:

Get Started
================

This section needs you have catsup installed.If you don't, please go and :ref:`Install it <installation>`

Init your site
---------------
It's pretty simple to create a site using catsup ::

    cd ~
    mkdir site
    cd site
    catsup init

After that, you need to change ``config.json`` ::

    vim config.json

Writing posts and pages
----------------

Let's write a post first ::

    vim posts/hello-world.md

Not, let's start writing the post ::

    # Hello, World!

    - time: 2013-08-25 23:30
    - tags: hello world

    ---

    Hello, World!
    This is my first post in catsup.

    ```python
    print("I love python")
    ```

Build your site
----------------
Now you have written your first post.Let's build your site ::

    cd ~/site
    catsup build

You can also preview your site using :ref:`Preview Server <preview-server>`
