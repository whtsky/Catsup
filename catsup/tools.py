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
from catsup.utils import load_posts, get_infos, write


def catsup_init():
    catsup_dir = os.getcwd()
    _input = ''
    try:
        _input = raw_input("Enter catsup directory(default"
                           " %s if you enter nothing):" % catsup_dir)
    except EOFError:
        return
    if _input:
        catsup_dir = _input
    if not os.path.exists(catsup_dir):
        if not os.makedirs(catsup_dir):
            print("Create directory failed, exiting...")
            sys.exit(0)
    os.chdir(catsup_dir)


def catsup_list_themes():
    pass


def catsup_install_theme():
    pass


def catsup_build():
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
    application = tornado.web.Application([
        (r'/webhook', handlers.WebhookHandler),
        ])
    print('Starting webhook at port %s' % options.port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
