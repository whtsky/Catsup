Changelog
==========

Version 0.3.1
--------------

+ Fix a bug on ``catsup install``

Version 0.3.0
--------------

+ Add multi-format post support
+ Add ``config.config.static_source``
+ Add ``config.config.static_output``
+ Support Non-meta post.
+ Support customize permalink for post
+ Support TXT format post.
+ Support HTML format post.
+ Support YAML format meta.
+ Rewrite `catsup install`
+ Correct the url for Twitter Card Support
+ Drop file-based cache system.
+ Improve description creator
+ Reorganize code.

Version 0.2.1
--------------

+ Fix build bugs.

Version 0.2.0
--------------

+ Support generate sitemap
+ Add `catsup watch` command
+ Add `catsup clean` command
+ Add cache for rendering markdown
+ Add cache for ``url_for``
+ Add cache for ``static_url``
+ Use Jinja2's Bytecode Cache
+ Don't generate analytics codes when running ``catsup server``
+ Display time cost for loading config and posts
+ Change json engine to `ujson`

Version 0.1.0
--------------

+ Use full md5 hash in ``static_url``
+ Add support for pages
+ Build to tempdir when running ``catsup server``
+ Add ``config.site.description``
+ Use ``config.comment.shortname`` to replace ``config.comment.disqus`` and ``config.comment.duoshuo``
+ Regenerate the site when your theme or posts changed when running ``catsup server``
+ Use local static file when running ``catsup server``
+ Post per page is defined by theme
+ Now catsup copy non-markdown files in source folder to deploy folder
+ Drop summary support
+ Drop escape markdown support
+ Add sub path support
+ Support customize any permalink
+ Rewrite generator, parser and server
+ Don't regenerate your site before deploy

Version 0.0.8
--------------

+ Rewrite tag and archive code
+ Add deploy support.(via git or rsync)

Version 0.0.7
--------------

Released on Feb. 7, 2013

+ Add pagination for writing theme
+ Rename excerpt to summary
+ Add theme utils
+ Support theme filters