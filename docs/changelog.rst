Changelog
==========

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