#coding=utf-8

import os
import config
import tornado.web
import tornado.ioloop
import tornado.escape
import misaka as m

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


md = m.Markdown(CatsupRender(),
    extensions=m.EXT_FENCED_CODE | m.EXT_NO_INTRA_EMPHASIS)


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
            post['content'] = md.render(content)
            break
    post['updated'] = os.stat(path).st_mtime
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
        file_name += '.md'
        try:
            post = load_post(file_name)
        except IOError:
            raise tornado.web.HTTPError(404)
        self.render('article.html', post=post)


posts = load_posts()

application = tornado.web.Application([
    (r'/', MainHandler),
    (r'/(.*)', ArticleHandler),
], posts = posts, autoescape=None, **config.settings)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        application.listen(sys.argv[1])
    else:
        application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
