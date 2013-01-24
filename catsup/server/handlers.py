#coding=utf-8
import os
import logging
import tornado.web

import catsup.build
from catsup.options import config, g


class BaseHandler(tornado.web.RequestHandler):
    def render_string(self, template_name, **kwargs):
        template = g.jinja.get_template(template_name)
        return template.render(**kwargs)

    def get_error_html(self, *args, **kwargs):
        return self.render_string('404.html')


class MainHandler(BaseHandler):
    def get(self, p=1):
        if p == '1':
            self.redirect('/', status=301)
        p = int(p)
        posts_num = len(g.posts)
        self.render('index.html', p=p, posts_num=posts_num)


class TagHandler(BaseHandler):
    def get(self, tag_name):
        tags = g.tags
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


class ArchiveHandler(BaseHandler):
    def get(self, archive_name):
        archives = g.archives
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


class FeedHandler(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "application/atom+xml")
        self.render('feed.xml')


class WebhookHandler(BaseHandler):
    def get(self):
        catsup.build.build()

    def post(self):
        """Webhook support for GitHub and Bitbucket.
        """
        logging.info('Updating posts...')
        current_dir = os.getcwd()
        os.chdir(config.config['posts'])
        if os.path.isdir('.git'):
            os.system('git pull')
        elif os.path.isdir('.hg'):
            os.system('hg pull')
        else:
            logging.warn("Your post folder is not a git/hg repo folder."
                         "Can not update your posts.")
        os.chdir(current_dir)
        catsup.build.build()


class PageHandler(BaseHandler):
    def get(self, filename):
        #Is this a post?
        posts = g.posts
        posts_num = len(posts)
        prev = next = None
        for i in range(posts_num):
            post = posts[i]
            if post.file_name == filename:
                if i:
                    prev = posts[i - 1]
                if (i + 1) < posts_num:
                    next = posts[i + 1]
                return self.render('article.html', post=post,
                    prev=prev, next=next)

        if filename in g.theme.pages:
            self.render(filename)
        else:
            raise tornado.web.HTTPError(404)
