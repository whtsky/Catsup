import os
import logging
import tornado.web
import tornado.httpserver
import tornado.ioloop

from catsup.options import g
import handlers


def preview(port):
    from catsup.build import load_jinja, load_theme_filters
    load_jinja()
    load_theme_filters(g.theme)
    from catsup.utils import load_posts
    load_posts()
    application = tornado.web.Application([
        (r'/', handlers.MainHandler),
        (r'/page/(.*?).html', handlers.MainHandler),
        (r'/archive/(.*?).html', handlers.ArchiveHandler),
        (r'/tag/(.*?).html', handlers.TagHandler),
        (r'/feed.xml', handlers.FeedHandler),
        (r'/(.*)', handlers.PageHandler),
        ], debug=True,
        static_path=os.path.join(g.theme.path, 'static'))
    logging.info('Starting preview server at port %s' % port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()


def webhook(port):
    application = tornado.web.Application([
        (r'/webhook', handlers.WebhookHandler),
        ])
    logging.info('Starting webhook server at port %s' % port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
