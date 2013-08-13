import os
import logging
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.autoreload

from tornado.log import access_log, app_log, gen_log
from catsup.generator import Generator
from catsup.logger import logger
from catsup.options import g
from catsup.utils import call


class CatsupServer(object):
    def __init__(self, settings, port):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.generator = Generator(settings)
        self.port = port

    @property
    def application(self):
        raise NotImplementedError()

    def silence_tornado(self):
        channel = logging.NullHandler()
        for logger in [access_log, app_log, gen_log]:
            logger.handlers = [channel]

    def prepare(self):
        pass

    def generate(self):
        self.generator.generate()

    def run(self):
        self.generate()
        self.prepare()
        self.silence_tornado()
        http_server = tornado.httpserver.HTTPServer(self.application,
                                                    io_loop=self.ioloop)
        http_server.listen(self.port)
        logger.info("Start server at port %s" % self.port)
        self.ioloop.start()


class PreviewServer(CatsupServer):
    def __init__(self, settings, port):
        super(PreviewServer, self).__init__(settings, port)
        self.generator = Generator(settings, base_url="http://127.0.0.1:%s/" % port)

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


class WebhookHandler(tornado.web.RequestHandler):
    def initialize(self, path, generate):
        self.path = path
        self.generate = generate

    def get(self):
        logger.info(logger.handlers)

        call("git pull", cwd=self.path)
        self.generate()
        self.write("success.")

    def post(self):
        self.get()


class WebhookServer(CatsupServer):
    @property
    def application(self):
        git_path = ""
        for path in ["/", self.generator.config.config.source]:
            path = os.path.abspath(os.path.join(
                g.cwdpath,
                path
            ))
            if os.path.exists(os.path.join(path, ".git")):
                git_path = path
                break
        if not git_path:
            logger.error("Can't find git repository.")
            exit(1)
        params = {
            "path": git_path,
            "generate": self.generate
        }
        return tornado.web.Application([
            (r"/.*?", WebhookHandler, params),
        ])
