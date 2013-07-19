import os
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.autoreload

from catsup.generator import Generator
from catsup.logger import logger
from catsup.options import g


class CatsupServer(object):
    def __init__(self, settings, port):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.generator = Generator(
            settings,
            base_url="http://127.0.0.1:%s/" % port
        )
        self.port = port

    @property
    def application(self):
        raise NotImplementedError()

    def prepare(self):
        pass

    def generate(self):
        self.generator.generate()

    def run(self):
        self.generate()
        self.prepare()
        http_server = tornado.httpserver.HTTPServer(self.application,
                                                    io_loop=self.ioloop)
        http_server.listen(self.port)
        logger.info("Start server at port %s" % self.port)
        self.ioloop.start()


class PreviewServer(CatsupServer):
    @property
    def application(self):
        params = {
            "path": g.output,
            "default_filename": "index.html"
        }
        return tornado.web.Application([
            (r"/(.*)", tornado.web.StaticFileHandler, params),
        ])

    def prepare(self):
        # Reload server when catsup modified.
        tornado.autoreload.start(self.ioloop)
        tornado.autoreload.add_reload_hook(self.generate)


class WebhookServer(CatsupServer):
    pass