#coding=utf-8

import os
import time
import sys
import shutil
import config
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.escape
import tornado.template
import misaka as m


from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name


class CatsupRender(m.HtmlRenderer, m.SmartyPants):
    def block_code(self, text, lang):
        if not lang:
            text = tornado.escape.xhtml_escape(text.strip())
            return '\n<pre><code>%s</code></pre>\n' % text
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter()
        return highlight(text, lexer, formatter)

    def autolink(self, link, is_email):
        if is_email:
            return '<a href="mailto:%(link)s">%(link)s</a>' % {'link': link}

        if '.' in link:
            name_extension = link.split('.')[-1].lower()
            if name_extension in ('jpg', 'png', 'git', 'jpeg'):
                return '<img src="%s" />' % link

        return '<a href="%s">%s</a>' % (link, link)

md = m.Markdown(CatsupRender(flags=m.HTML_ESCAPE | m.HTML_USE_XHTML),
    extensions=m.EXT_FENCED_CODE | m.EXT_NO_INTRA_EMPHASIS | m.EXT_AUTOLINK |
        m.EXT_STRIKETHROUGH | m.EXT_SUPERSCRIPT)


def load_post(file_name):
    '''Load a post.return a dict.
    '''
    path = os.path.join(config.posts_path, file_name)
    file = open(path, 'r')
    post = {'file_name': file_name[:-3],
            'tags': [],
            'date': file_name[:10]}
    while True:
        line = file.readline()
        if line.startswith('#'):
            post['title'] = line[1:].strip()
        elif 'tags' in line.lower():
            for tag in line.split(':')[-1].strip().split(','):
                post['tags'].append(tag.strip())
        elif line.startswith('---'):
            content = '\n'.join(file.readlines())
            if isinstance(content, str):
                content = content.decode('utf-8')
            post['content'] = md.render(content)
            post['updated'] = os.stat(path).st_ctime
            updated_xml = time.gmtime(post['updated'])
            post['updated_xml'] = time.strftime('%Y-%m-%dT%H:%M:%SZ',
                updated_xml)
            return post


def load_posts():
    '''load all the posts.return a list.
    Sort with filename.
    '''
    post_files = os.listdir(config.posts_path)
    post_files.sort(reverse=True)
    posts = []
    for file_name in post_files:
        if '.md' in file_name:
            post = load_post(file_name)
            posts.append(post)
    return posts


def get_infos(posts):
    """return the tag list and archive list.
    """
    tags = {}
    archives = {}
    for post in posts:
        for tag in post['tags']:
            if tag in tags:
                tags[tag].append(post)
            else:
                tags[tag] = [post]
        year = post['date'][:4]
        if year in archives:
            archives[year].append(post)
        else:
            archives[year] = [post]

    return sorted(tags.items(), key=lambda x: len(x[1]), reverse=True),\
        sorted(archives.items(), key=lambda x: x[0], reverse=True)


class BaseHandler(tornado.web.RequestHandler):
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
        prev = next = None
        for i, tag in enumerate(self.settings['tags']):
            if tag[0] == tag_name:
                i += 1
                if i < len(self.settings['tags']):
                    next = self.settings['tags'][i]
                return self.render('tag.html', tag=tag,
                    prev=prev, next=next)
            prev = tag

        raise tornado.web.HTTPError(404)


class ArchivesHandler(BaseHandler):
    def get(self):
        self.render('archives.html')


class ArchiveHandler(BaseHandler):
    def get(self, archive_name):
        prev = next = None
        for i, archive in enumerate(self.settings['archives']):
            if archive[0] == archive_name:
                i += 1
                if i < len(self.settings['archives']):
                    next = self.settings['archives'][i]
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
        loader = tornado.template.Loader(config.common_template_path,
            autoescape=None)
        p = loader.load("feed.xml").generate(posts=self.settings['posts'],
            handler=config)
        self.write(p)


class SitemapHandler(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        loader = tornado.template.Loader(config.common_template_path,
            autoescape=None)
        p = loader.load("sitemap.txt").generate(posts=self.settings['posts'],
            handler=config, tags=self.settings['tags'],
            archives=self.settings['archives'])
        self.write(p)


class WebhookHandler(BaseHandler):
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


posts = load_posts()
tags, archives = get_infos(posts)


def write(file_name, page):
    file_path = os.path.join(config.deploy_path, file_name)
    open(file_path, 'w').write(page)


def deploy():
    posts = load_posts()
    tags, archives = get_infos(posts)
    posts_num = len(posts)
    config.settings['tags'] = tags
    config.settings['archives'] = archives
    
    if os.path.exists(config.deploy_path):
        shutil.rmtree(config.deploy_path)

    os.makedirs(config.deploy_path)

    loader = tornado.template.Loader(config.common_template_path,
        autoescape=None)

    print('Generating sitemap')
    page = loader.load("sitemap.txt").generate(posts=posts, handler=config,
        tags=tags, archives=archives)
    write('sitemap.txt', page)

    print('Generating atom')
    page = loader.load("feed.xml").generate(posts=posts, handler=config)
    write('feed.xml', page)

    loader = tornado.template.Loader(config.settings['template_path'],
        autoescape=None)

    print('Start generating index pages')
    generator = loader.load("index.html")
    p = 0
    while posts_num > p * config.settings['post_per_page']:
        p += 1
        print('Start generating page %s' % p)
        page = generator.generate(posts=posts, handler=config,
            p=p)
        write('page_%s.html' % p, page)

    index_1 = os.path.join(config.deploy_path, 'page_1.html')
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
        page = generator.generate(post=post, handler=config,
            prev=prev, next=next)
        write('%s.html' % post['file_name'], page)
        prev, post, next = post, next, len(posts) and posts.pop() or None

    print('Start generating tag pages')
    generator = loader.load("tag.html")
    prev = None
    for i, tag in enumerate(tags):
        print('Generating tag %s' % tag[0])
        i += 1
        next = i < len(tags) and tags[i] or None
        page = generator.generate(tag=tag, prev=prev,
            next=next, handler=config)
        write('tag_%s.html' % tag[0], page)
        prev = tag

    print('Start generating archive pages')
    generator = loader.load("archive.html")
    prev = None
    for i, archive in enumerate(archives):
        print('Generating archive %s' % archive[0])
        i += 1
        next = i < len(archives) and archives[i] or None
        page = generator.generate(archive=archive, prev=prev,
            next=next, handler=config)
        write('archive_%s.html' % archive[0], page)
        prev = archive

    print('Start generating other pages')
    for p in ('404', 'tags', 'archives', 'links'):
        page = loader.load("%s.html" % p).generate(handler=config)
        write('%s.html' % p, page)

    print('Copying static files.')
    deploy_static_dir = os.path.join(config.deploy_path, 'static')
    if os.path.exists(deploy_static_dir):
        shutil.rmtree(deploy_static_dir)
    shutil.copytree(config.settings['static_path'], deploy_static_dir)
    os.chdir(config.deploy_path)
    os.system('cp static/favicon.ico ./')
    os.system('cp static/robots.txt ./')

    print('Done.')


def update_posts():
    os.chdir(config.posts_path)
    if os.path.isdir(os.path.join(config.posts_path, '.git')):
        os.system('git pull')
    elif os.path.isdir(os.path.join(config.posts_path, '.hg')):
        os.system('hg pull')


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print('Useage: catsup.py server/deploy/webhook')
        sys.exit(0)
    cmd = args[1]
    del args[1]
    if cmd == 'server':
        application = tornado.web.Application([
            (r'/', MainHandler),
            (r'/page_(.*?).html', MainHandler),
            (r'/archives.html', ArchivesHandler),
            (r'/archive_(.*?).html', ArchiveHandler),
            (r'/tags.html', TagsHandler),
            (r'/tag_(.*?).html', TagHandler),
            (r'/links.html', LinksHandler),
            (r'/feed.xml', FeedHandler),
            (r'/sitemap.txt', SitemapHandler),
            (r'/webhook', WebhookHandler),
            (r'/(.*).html', ArticleHandler),
            (r'/.*', ErrorHandler),
        ], autoescape=None, posts=posts, tags=tags, archives=archives,
        **config.settings)
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
        http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
