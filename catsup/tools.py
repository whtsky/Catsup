#coding=utf-8
import os
import sys
import shutil
import logging
import tornado
import tornado.httpserver
import tornado.ioloop

from tornado.options import options
from catsup import handlers
from catsup.config import save_config_file
from catsup.utils import load_posts, get_infos, write


def catsup_init():
    catsup_dir = os.getcwd()
    if len(sys.argv) > 1:
        # Please note that sys.argv.pop(1) had been executed before here.
        # If length of sys.argv > 1, user runned command "catsup init xxx"
        # instead of "catsup init". And now sys.argv[1] == xxx,
        # we regard xxx as a directory relatively to current working directory
        # to initialize catsup.
        catsup_dir = os.path.join(catsup_dir, sys.argv[1])
    ini_path = os.path.join(catsup_dir, 'config.ini')

    if os.path.exists(ini_path):
        print("These is a config.ini in current directory(%s), "
              "please check whether you have set up catsup before." % catsup_dir)
        print("If you really want to setup catsup in here, please backup "
              "and remove all files here and run \"catsup init\" again.")
        return

    options.posts_path = os.path.join(catsup_dir, 'posts')
    options.themes_path = os.path.join(catsup_dir, 'themes')

    if os.path.exists(options.posts_path):
        shutil.rmtree(options.posts_path)
    if os.path.exists(options.themes_path):
        shutil.rmtree(options.themes_path)

    os.makedirs(os.path.join(catsup_dir, 'posts'))
    #package_themes = os.path.join(options.catsup_path, 'themes')
    #shutil.copytree(package_themes, options.themes_path)

    save_config_file(ini_path)
    print("catsup init success!")
    print("Please edit the generated config.ini to configure your blog. "
          "Or you can run \"catsup config\" to generate your configuration.")

def catsup_config():
    catsup_dir = os.getcwd()

    _input = raw_input("Enter catsup directory(default"
                           " %s if you enter nothing):" % catsup_dir)
    if _input:
        catsup_dir = _input
    if not os.path.exists(catsup_dir):
        if not os.makedirs(catsup_dir):
            print("Create directory failed, exiting...")
            sys.exit(0)
    os.chdir(catsup_dir)
    ini_path = os.path.join(catsup_dir, 'config.ini')

    if not os.path.exists(ini_path):
        print("No config.ini found in this directory(%s), "
              "please run \"catsup init\" first.")
        sys.exit(0)

    _input = raw_input("Enter your site title:")
    if not _input:
        print("Site title is null, exiting...")
        sys.exit(0)
    options.site_title = _input

    _input = raw_input("Enter your site description: ")
    options.site_description = _input

    _input = raw_input("Enter your site url: ")
    options.site_url = _input

    _input = raw_input("Enter your static resources url"
                       "(default /static if you enter nothing): ")
    if _input:
        options.static_url = _input

    _input = raw_input("Enter your rss feed url"
                       "(default /feed.xml if you enter nothing): ")
    if _input:
        options.feed = _input

    _input = raw_input("Choose your comment system, "
                       "enter 1 for disqus, 2 for duoshuo: ")
    if _input == '1':
        options.comment_system = 'disqus'
    elif _input == '2':
        options.comment_system = 'duoshuo'
    else:
        options.comment_system = 'disqus'

    if options.comment_system == 'disqus':
        _input = raw_input("Enter your disqus shortname: ")
        options.disqus_shortname = _input
    elif options.comment_system == 'duoshuo':
        _input = raw_input("Enter your duoshuo shortname: ")
        options.duoshuo_shortname = _input

    _input = raw_input("Enter 1 if you want to leave "
                       "date in permalink, 0 if not: ")
    if _input == 0:
        options.date_in_permalink = False
    else:
        options.date_in_permalink = True

    _input = raw_input("Enter 1 if you want to display "
                       "post excerpt in homepage, 0 if not: ")
    if _input == 0:
        options.excerpt_index = False
    else:
        options.excerpt_index = True

    _input = raw_input("How many posts per page do you want: ")
    options.post_per_page = int(_input)

    options.twitter = raw_input("Enter your twitter username: ")
    options.github = raw_input("Enter your github username: ")
    options.google_analytics = raw_input("Enter your Google Analytics ID: ")
    save_config_file(ini_path)


def catsup_list_themes():
    catsup_dir = os.getcwd()
    cwd_themes = os.path.join(catsup_dir, 'themes')
    global_themes = os.path.join(options.catsup_path, 'themes')
    themes = set()
    themes_dir = os.listdir(global_themes)
    for name in themes_dir:
        dir_path = os.path.join(global_themes, name)
        if os.path.isdir(dir_path):
            themes.add(name)
    if os.path.exists(cwd_themes):
        themes_dir = os.listdir(cwd_themes)
        for name in themes_dir:
            dir_path = os.path.join(cwd_themes, name)
            if os.path.isdir(dir_path):
                themes.add(name)
    print('Available themes: \n')
    for name in themes:
        print(name)


def catsup_install_theme():
    if len(sys.argv) < 2:
        print('Usage: catsup install theme_name')
        sys.exit(0)
    catsup_dir = os.getcwd()
    cwd_themes = os.path.join(catsup_dir, 'themes')
    global_themes = os.path.join(options.catsup_path, 'themes')
    if not options.config_loaded:
        print('Current working directory is not a catsup directory.')
        sys.exit(0)
    if not os.path.exists(cwd_themes):
        os.makedirs(cwd_themes)
    theme_name = sys.argv.pop(1)
    if theme_name.endswith('.git'):
        # The theme is a git repo
        os.chdir(cwd_themes)
        os.system('git clone %s' % theme_name)
        print('Theme successfully installed.')
        sys.exit(0)
    theme_path = os.path.join(global_themes, theme_name)
    install_path = os.path.join(cwd_themes, theme_name)
    if os.path.isdir(install_path):
        print('Theme %s has been installed.' % theme_name)
        sys.exit(0)
    if os.path.isdir(theme_path):
        # The theme is in global themes directory
        # simply copy it
        shutil.copytree(theme_path, install_path)
        print('Theme %s successfully installed' % theme_name)
    else:
        print('No available theme named %s' % theme_name)


def catsup_build():
    if not options.config_loaded:
        print("Please run \"catsup init\" first.")
        sys.exit(0)
    logging.info('Building your blog..')
    posts = load_posts()
    tags, archives = get_infos(posts)
    posts_num = len(posts)

    options.tags = tags
    options.posts = posts
    options.archives = archives

    if os.path.exists(options.build_path):
        shutil.rmtree(options.build_path)

    os.makedirs(options.build_path)

    loader = tornado.template.Loader(options.common_template_path,
        autoescape=None)

    logging.info('Generating sitemap')
    page = loader.load("sitemap.txt").generate(posts=posts, tags=tags,
        archives=archives, config=options)
    write('sitemap.txt', page)

    logging.info('Generating atom')
    page = loader.load("feed.xml").generate(posts=posts, config=options)
    write('feed.xml', page)

    loader = tornado.template.Loader(options.template_path,
        autoescape=None)

    logging.info('Start generating index pages')
    page_path = os.path.join(options.build_path, 'page')
    if os.path.exists(page_path):
        shutil.rmtree(page_path)
    os.makedirs(page_path)
    generator = loader.load("index.html")
    p = 0
    while posts_num > p * options.post_per_page:
        p += 1
        logging.info('Start generating page %s' % p)
        page = generator.generate(posts=posts, p=p, config=options)
        pager_file = os.path.join(page_path, "%s.html" % p)
        write(pager_file, page)

    index_1 = os.path.join(page_path, '1.html')
    index = os.path.join(options.build_path, 'index.html')
    os.rename(index_1, index)

    logging.info('Start generating articles')
    generator = loader.load("article.html")
    posts.reverse()
    prev = None
    post = posts.pop()
    next = len(posts) and posts.pop() or None
    while post:
        logging.info('Generating %s' % post.file_name)
        page = generator.generate(post=post, prev=prev,
            next=next, config=options)
        write('%s.html' % post.file_name, page)
        prev, post, next = post, next, len(posts) and posts.pop() or None

    logging.info('Start generating tag pages')
    tag_path = os.path.join(options.build_path, 'tag')
    if os.path.exists(tag_path):
        shutil.rmtree(tag_path)
    os.makedirs(tag_path)
    generator = loader.load("tag.html")
    prev = None
    for i, tag in enumerate(tags):
        logging.info('Generating tag %s' % tag.name)
        i += 1
        next = i < len(tags) and tags[i] or None
        page = generator.generate(tag=tag, prev=prev,
            next=next, config=options)
        tag_file = os.path.join(tag_path, "%s.html" % tag.name.lower())
        write(tag_file, page)
        prev = tag

    logging.info('Start generating archive pages')
    archive_path = os.path.join(options.build_path, 'archive')
    if os.path.exists(archive_path):
        shutil.rmtree(archive_path)
    os.makedirs(archive_path)
    generator = loader.load("archive.html")
    prev = None
    for i, archive in enumerate(archives):
        logging.info('Generating archive %s' % archive.name)
        i += 1
        next = i < len(archives) and archives[i] or None
        page = generator.generate(archive=archive, prev=prev,
            next=next, config=options)
        archive_file = os.path.join(archive_path, "%s.html" % archive.name)
        write(archive_file, page)
        prev = archive

    logging.info('Start generating other pages')
    for p in ('404', 'tags', 'archives', 'links'):
        page = loader.load("%s.html" % p).generate(config=options)
        write('%s.html' % p, page)

    logging.info('Copying static files.')
    build_static_dir = os.path.join(options.build_path, 'static')
    if os.path.exists(build_static_dir):
        shutil.rmtree(build_static_dir)
    shutil.copytree(options.static_path, build_static_dir)
    os.chdir(options.build_path)

    # Favicon, use favicon.ico in _posts directory default
    # or fallback to the one in static directory
    favicon_file = os.path.join(options.posts_path, 'favicon.ico')
    if os.path.exists(favicon_file):
        os.system('cp %s ./' % favicon_file)
    else:
        os.system('cp static/favicon.ico ./')

    # Robots.txt, use robots.txt in _posts directory default
    # or fallback to the one in static directory
    robots_file = os.path.join(options.posts_path, 'robots.txt')
    if os.path.exists(robots_file):
        os.system('cp %s ./' % robots_file)
    else:
        os.system('cp static/robots.txt ./')

    logging.info('Done.')


def catsup_server():
    if not options.config_loaded:
        print("Please run \"catsup init\" first.")
        sys.exit(0)
    posts = load_posts()
    tags, archives = get_infos(posts)
    settings = dict(
        autoescape=None,
        static_path=options.static_path,
        template_path=options.template_path,
    )
    application = tornado.web.Application([
        (r'/', handlers.MainHandler),
        (r'/page/(.*?).html', handlers.MainHandler),
        (r'/archives.html', handlers.ArchivesHandler),
        (r'/archive/(.*?).html', handlers.ArchiveHandler),
        (r'/tags.html', handlers.TagsHandler),
        (r'/tag/(.*?).html', handlers.TagHandler),
        (r'/links.html', handlers.LinksHandler),
        (r'/feed.xml', handlers.FeedHandler),
        (r'/sitemap.txt', handlers.SitemapHandler),
        (r'/(.*).html', handlers.ArticleHandler),
        (r'/.*', handlers.ErrorHandler),
        ], posts=posts, tags=tags, archives=archives, **settings)
    print('Starting server at port %s' % options.port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

def catsup_webhook():
    if not options.config_loaded:
        print("Please run \"catsup init\" first.")
        sys.exit(0)
    application = tornado.web.Application([
        (r'/webhook', handlers.WebhookHandler),
        ])
    print('Starting webhook at port %s' % options.port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
