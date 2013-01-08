#coding=utf-8
import tornado.web
import tornado.template
from tornado.options import options
import catsup.tools

from catsup.utils import update_posts


class BaseHandler(tornado.web.RequestHandler):
    def render_string(self, template_name, **kwargs):
        options.tags = self.settings['tags']
        options.posts = self.settings['posts']
        options.archives = self.settings['archives']
        # access config directly
        kwargs["config"] = options
        return super(BaseHandler, self).render_string(template_name, **kwargs)

    def get_error_html(self, *args, **kwargs):
        return self.render_string('404.html')


class MainHandler(BaseHandler):
    def get(self, p=1):
        if p == '1':
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
            if post.file_name == file_name:
                if i:
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
            if tag.name == tag_name:
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
            if archive.name == archive_name:
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
        loader = tornado.template.Loader(options.common_template_path,
            autoescape=None)
        p = loader.load("feed.xml").generate(posts=self.settings['posts'],
            config=options)
        self.write(p)


class SitemapHandler(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain")
        loader = tornado.template.Loader(options.common_template_path,
            autoescape=None)
        p = loader.load("sitemap.txt").generate(posts=self.settings['posts'],
            config=options, tags=self.settings['tags'],
            archives=self.settings['archives'])
        self.write(p)


class ErrorHandler(BaseHandler):
    def prepare(self):
        raise tornado.web.HTTPError(404)


class WebhookHandler(BaseHandler):
    def get(self):
        catsup.tools.catsup_build()

    def post(self):
        """Webhook support for GitHub and Bitbucket.
        """
        update_posts()
        catsup.tools.catsup_build()