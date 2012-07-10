#coding=utf-8

import os
import time
import config
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import tornado.escape
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


md = m.Markdown(CatsupRender(flags=m.HTML_ESCAPE | m.HTML_USE_XHTML),
    extensions=m.EXT_FENCED_CODE | m.EXT_NO_INTRA_EMPHASIS | m.EXT_AUTOLINK)


def load_post(file_name):
    '''Load a post.return a dict.
    '''
    path = os.path.join(config.posts_path, file_name)
    file = open(path, 'r')
    post = {'file_name': file_name[:-3]}
    while True:
        line = file.readline()
        if line.startswith('#'):
            post['title'] = line.replace('#', '')
        elif 'date' in line.lower():
            post['date'] = line.split(':')[-1].replace(' ', '')
        elif line.startswith('---'):
            content = '\n'.join(file.readlines())
            if isinstance(content, str):
                content = content.decode('utf-8')
            post['content'] = md.render(content)
            break
    post['updated'] = os.stat(path).st_ctime
    updated_xml = time.gmtime(post['updated'])
    post['updated_xml'] = time.strftime('%Y-%m-%dT%H:%M:%SZ', updated_xml)
    return post


def load_posts():
    '''load all the posts.return a list.
    sort with mtime.
    '''
    post_files = os.listdir(config.posts_path)
    posts = []
    for file_name in post_files:
        if '.md' in file_name:
            post = load_post(file_name)
            posts.append(post)
    posts.sort(key=lambda x: x['updated'], reverse=True)
    return posts


class BaseHandler(tornado.web.RequestHandler):
    def get_error_html(self, *args, **kwargs):
        return self.render_string('404.html')


class MainHandler(BaseHandler):
    def get(self):
        p = self.get_argument('p', default=0)
        if p > len(self.settings['posts']):
            raise tornado.web.HTTPError(404)
        self.render('index.html', posts=self.settings['posts'], p=p)


class ArticleHandler(BaseHandler):
    def get(self, file_name):
        for post in self.settings['posts']:
            if post['file_name'] == file_name:
                return self.render('article.html', post=post)
        raise tornado.web.HTTPError(404)



class FeedHandler(BaseHandler):
    def get(self):
        posts = self.settings['posts'][:3]
        self.render('feed.xml', posts=posts)


class ReloadHandler(BaseHandler):
    def post(self):
        """Github Post-Receive Hooks support.
        """
        if self.request.remote_ip not in config.github_ips:
            pass
        payload = self.get_argument('payload')
        payload = tornado.escape.json_decode(payload)
        if payload['repository']['owner']['name'] != config.github:
            pass
        os.chdir(config.posts_path)
        os.system('git pull')
        self.settings['posts'] = load_posts()

posts = load_posts()

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/feed', FeedHandler),
    (r'/reload', ReloadHandler),
    (r'/(.*)', ArticleHandler),
], posts = posts, autoescape=None, **config.settings)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
