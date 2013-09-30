.. _upgrading:

Upgrading to Newer Releases
============================

Catsup itself is changing like any software is changing over time.  Most of
the changes are the nice kind, the kind where you don't have to change
anything in your site to profit from a new release.

However every once in a while there are changes that do require some
changes in your site.

This section of the documentation enumerates all the changes in Catsup from
release to release and how you can change your site to have a painless
updating experience.

If you want to use the `easy_install` command to upgrade your Catsup
installation, make sure to pass it the ``-U`` parameter::

    $ easy_install -U catsup

Version 0.2.0
----------------

Catsup adds an cache system since 0.2.0 .

Cache files are stored in ``.catsup-cache`` folder, so if you are using git to organize your site and
want to ignore the cache files, add the following line to your ``.gitignore`` file ::

    .catsup-cache

