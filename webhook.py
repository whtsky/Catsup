#!/usr/bin/env python
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.options
import os
import config

from tornado.options import define, options

define("port", default=80, help="run on the given port", type=int)


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
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    os.chdir(config.catsup_path)
    os.system('chmod +x catsup-static.py')
    tornado.ioloop.IOLoop.instance().start()
