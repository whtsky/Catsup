#!/usr/bin/env python
import tornado.httpserver
import tornado.web
import tornado.ioloop
import os
import config


def update_posts():
    os.chdir(config.posts_path)
    if os.path.isdir(os.path.join(config.posts_path, '.git')):
        os.system('git pull')
    elif os.path.isdir(os.path.join(config.posts_path, '.hg')):
        os.system('hg pull')


class WebhookHandler(tornado.web.RequestHandler):
    def post(self):
        """Webhook support for GitHub and Bitbucket.
        """
        update_posts()
        os.chdir(config.catsup_path)
        os.system('./catsup-static.py')


application = tornado.web.Application([
    (r'/webhook', WebhookHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(2331)
    os.chdir(config.catsup_path)
    os.system('chmod +x catsup-static.py')
    tornado.ioloop.IOLoop.instance().start()
