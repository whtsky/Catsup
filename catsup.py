#coding=utf-8

import os
import sys
import shutil
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.escape
import tornado.template


from tornado.options import define, options
from tornado.util import ObjectDict
from utils import load_config, load_posts, get_infos

define("port", default=8888, help="run on the given port", type=int)

config = load_config()
# posts = load_posts(config)
# tags, archives = get_infos(posts)

class BaseHandler(tornado.web.RequestHandler):

    def render_string(self, template_name, **kwargs):
        config.tags = self.settings['tags']
        config.posts = self.settings['posts']
        config.archives = self.settings['archives']
        # access config directly
        kwargs["config"] = config
        return super(BaseHandler, self).render_string(template_name,**kwargs)

    def get_error_html(self, *args, **kwargs):
        return self.render_string('404.html')


class MainHandler(BaseHandler):
    def get(self, p=1):
        if p == '1':  # /page_1.html
            self.redirect('/', status=301)
        p = int(p)
        self.render('index.html', posts=self.settings['posts'], p=p)


class ArticleHandler(BaseHandler):
    def get(self, file_name):
        posts = self.settings['posts']
        posts_num = len(posts)
        prev = next = None
        for i in range(posts_num):
            post = posts[i]
            if post['file_name'] == file_name:
                if i:  # i>0
                    prev = posts[i - 1]
                if (i + 1) < posts_num:
                    next = posts[i + 1]
                return self.render('article.html', post=post,
                    prev=prev, next=next)
        raise tornado.web.HTTPError(404)


class TagsHandler(BaseHandler):
    def get(self):
        self.render('tags.html')


class TagHandler(BaseHandler):
    def get(self, tag_name):
        tags = self.settings['tags']
        prev = next = None
        for i, tag in enumerate(tags):
            if tag[0] == tag_name:
                i += 1
                if i < len(tags):
                    next = tags[i]
                return self.render('tag.html', tag=tag,
                    prev=prev, next=next)
            prev = tag

        raise tornado.web.HTTPError(404)


class ArchivesHandler(BaseHandler):
    def get(self):
        self.render('archives.html')


class ArchiveHandler(BaseHandler):
    def get(self, archive_name):
        archives = self.settings['archives']
        prev = next = None
        for i, archive in enumerate(archives):
            if archive[0] == archive_name:
                i += 1
                if i < len(archives):
                    next = archives[i]
                return self.render('archive.html', archive=archive,
                    prev=prev, next=next)
            prev = archive
        raise tornado.web.HTTPError(404)


class LinksHandler(BaseHandler):
    def get(self):
        self.render('links.html')


class FeedHandler(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "application/atom+xml")
        loader = tornado.template.Loader(config['common_template_path'],
            autoescape=None)
        p = loader.load("feed.xml").generate(posts=self.settings['posts'], 
            config=config)
        self.write(p)


class SitemapHandler(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        loader = tornado.template.Loader(config['common_template_path'],
            autoescape=None)
        p = loader.load("sitemap.txt").generate(posts=self.settings['posts'],
            config=config, tags=self.settings['tags'],
            archives=self.settings['archives'])
        self.write(p)


class WebhookHandler(BaseHandler):
    def get(self):
        deploy()

    def post(self):
        """Webhook support for GitHub and Bitbucket.
        """
        update_posts()
        if 'tags' in self.settings:
            posts = load_posts()
            tags, archives = get_infos(posts)
            self.settings['posts'] = posts
            self.settings['tags'] = tags
            self.settings['archives'] = archives
        else:
            deploy()


class ErrorHandler(BaseHandler):
    def prepare(self):
        raise tornado.web.HTTPError(404)


def write(file_name, page):
    if not file_name.startswith(config['deploy_path']):
        file_path = os.path.join(config['deploy_path'], file_name)
    else:
        file_path = file_name
    open(file_path, 'w').write(page)


def deploy():
    posts = load_posts(config)
    tags, archives = get_infos(posts)
    posts_num = len(posts)
    config['posts'] = posts
    config['tags'] = tags
    config['archives'] = archives

    if os.path.exists(config.deploy_path):
        shutil.rmtree(config.deploy_path)

    os.makedirs(config.deploy_path)

    loader = tornado.template.Loader(config.common_template_path,
        autoescape=None)

    print('Generating sitemap')
    page = loader.load("sitemap.txt").generate(posts=posts, tags=tags, 
        archives=archives, config=config)
    write('sitemap.txt', page)

    print('Generating atom')
    page = loader.load("feed.xml").generate(posts=posts, config=config)
    write('feed.xml', page)

    loader = tornado.template.Loader(config['template_path'],
        autoescape=None)

    print('Start generating index pages')
    page_path = os.path.join(config.deploy_path, 'page')
    if os.path.exists(page_path):
        shutil.rmtree(page_path)
    os.makedirs(page_path)
    generator = loader.load("index.html")
    p = 0
    while posts_num > p * config['post_per_page']:
        p += 1
        print('Start generating page %s' % p)
        page = generator.generate(posts=posts, p=p, config=config)
        pager_file = os.path.join(page_path, "%s.html" % p)
        write(pager_file, page)

    index_1 = os.path.join(page_path, '1.html')
    index = os.path.join(config.deploy_path, 'index.html')
    os.rename(index_1, index)

    print('Start generating articles')
    generator = loader.load("article.html")
    posts.reverse()
    prev = None
    post = posts.pop()
    next = len(posts) and posts.pop() or None
    while post:
        print('Generating %s' % post['file_name'])
        page = generator.generate(post=post, prev=prev, 
            next=next, config=config)
        write('%s.html' % post['file_name'], page)
        prev, post, next = post, next, len(posts) and posts.pop() or None

    print('Start generating tag pages')
    tag_path = os.path.join(config.deploy_path, 'tag')
    if os.path.exists(tag_path):
        shutil.rmtree(tag_path)
    os.makedirs(tag_path)
    generator = loader.load("tag.html")
    prev = None
    for i, tag in enumerate(tags):
        print('Generating tag %s' % tag[0])
        i += 1
        next = i < len(tags) and tags[i] or None
        page = generator.generate(tag=tag, prev=prev,
            next=next, config=config)
        tag_file = os.path.join(tag_path, "%s.html" % tag[0].lower())
        write(tag_file, page)
        prev = tag

    print('Start generating archive pages')
    archive_path = os.path.join(config.deploy_path, 'archive')
    if os.path.exists(archive_path):
        shutil.rmtree(archive_path)
    os.makedirs(archive_path)
    generator = loader.load("archive.html")
    prev = None
    for i, archive in enumerate(archives):
        print('Generating archive %s' % archive[0])
        i += 1
        next = i < len(archives) and archives[i] or None
        page = generator.generate(archive=archive, prev=prev,
            next=next, config=config)
        archive_file = os.path.join(archive_path, "%s.html" % archive[0])
        write(archive_file, page)
        prev = archive

    print('Start generating other pages')
    for p in ('404', 'tags', 'archives', 'links'):
        page = loader.load("%s.html" % p).generate(config=config)
        write('%s.html' % p, page)

    print('Copying static files.')
    deploy_static_dir = os.path.join(config.deploy_path, 'static')
    if os.path.exists(deploy_static_dir):
        shutil.rmtree(deploy_static_dir)
    shutil.copytree(config['static_path'], deploy_static_dir)
    os.chdir(config.deploy_path)
    # Favicon, use favicon.ico in _posts directory default or fallback to the one in static directory
    favicon_file = os.path.join(config.posts_path, 'favicon.ico')
    if os.path.exists(favicon_file):
        os.system('cp %s ./' % favicon_file)
    else:
        os.system('cp static/favicon.ico ./')
    # Robots.txt, use robots.txt in _posts directory default or fallback to the one in static directory
    robots_file = os.path.join(config.posts_path, 'robots.txt')
    if os.path.exists(robots_file):
        os.system('cp %s ./' % robots_file)
    else:
        os.system('cp static/robots.txt ./')

    print('Done.')


def update_posts():
    os.chdir(config['posts_path'])
    if os.path.isdir(os.path.join(config['posts_path'], '.git')):
        os.system('git pull')
    elif os.path.isdir(os.path.join(config['posts_path'], '.hg')):
        os.system('hg pull')


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('Useage: catsup.py server/deploy/webhook')
        sys.exit(0)
    cmd = args[1]
    del args[1]
    if cmd == 'server':
        posts = load_posts(config)
        tags, archives = get_infos(posts)
        application = tornado.web.Application([
            (r'/', MainHandler),
            (r'/page/(.*?).html', MainHandler),
            (r'/archives.html', ArchivesHandler),
            (r'/archive/(.*?).html', ArchiveHandler),
            (r'/tags.html', TagsHandler),
            (r'/tag/(.*?).html', TagHandler),
            (r'/links.html', LinksHandler),
            (r'/feed.xml', FeedHandler),
            (r'/sitemap.txt', SitemapHandler),
            (r'/webhook', WebhookHandler),
            (r'/(.*).html', ArticleHandler),
            (r'/.*', ErrorHandler),
        ], autoescape=None, posts=posts, tags=tags, archives=archives,
        **config)
    elif cmd == 'deploy':
        deploy()
    elif cmd == 'webhook':
        application = tornado.web.Application([
            (r'/webhook', WebhookHandler),
        ])
    else:
        print('Unknow Command: %s' % cmd)
        sys.exit(0)

    if 'application' in locals():
        tornado.options.parse_command_line(args)
        if cmd == 'server':
            print('Starting server at port %s' % options.port)
        elif cmd == 'webhook':
            print('Starting webhook at port %s' % options.port)
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
