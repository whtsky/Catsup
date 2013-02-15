import os
import logging
import tornado.web
import tornado.httpserver
import tornado.ioloop

from catsup.options import g, config
import handlers


def preview(port):
    from catsup.build import build
    build()
    os.chdir(config.config.output)
    import SimpleHTTPServer
    import SocketServer

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    httpd = SocketServer.TCPServer(("", int(port)), Handler)

    logging.info("serving at port %s" % port)
    httpd.serve_forever()


def webhook(port):
    application = tornado.web.Application([
        (r'/webhook', handlers.WebhookHandler),
        ])
    logging.info('Starting webhook server at port %s' % port)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()
