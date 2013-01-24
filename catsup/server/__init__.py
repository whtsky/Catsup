import os
import logging
import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import options

from catsup.options import g
import handlers


def preview():
    from catsup.build import load_jinja
    load_jinja()
    from catsup.utils import load_posts
    load_posts()
    application = tornado.web.Application([
        (r'/', handlers.MainHandler),
        (r'/page/(.*?).html', handlers.MainHandler),
        (r'/archive/(.*?).html', handlers.ArchiveHandler),
        (r'/tag/(.*?).html', handlers.TagHandler),
        (r'/feed.xml', handlers.FeedHandler),
        (r'/(.*).html', handlers.PageHandler),
        ],
        static_path=os.path.join(g.theme.path, 'static'))
    logging.info('Starting preview server at port %s' % options.port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


def webhook():
    application = tornado.web.Application([
        (r'/webhook', handlers.WebhookHandler),
        ])
    logging.info('Starting webhook server at port %s' % options.port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
