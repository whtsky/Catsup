import os
import catsup
import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.autoreload

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from catsup.generator import Generator
from catsup.logger import logger
from catsup.options import g
from catsup.utils import call


class CatsupEventHandler(FileSystemEventHandler):
    def __init__(self, generator):
        self.generator = generator

    def on_any_event(self, event):
        logger.info("Captured a file change. Regenerate..")
        try:
            self.generator.generate()
        except:
            logger.error("Error when generating:", exc_info=True)


class CatsupHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Server", "Catsup/%s" % catsup.__version__)

    def log_exception(self, typ, value, tb):
        pass


class WebhookHandler(CatsupHandler):
    def initialize(self, path, generate):
        self.path = path
        self.generate = generate

    def get(self):
        call("git pull", cwd=self.path)
        self.generate()
        self.write("success.")

    def post(self):
        self.get()


class StaticFileHandler(CatsupHandler, tornado.web.StaticFileHandler):
    pass


class CatsupServer(object):
    def __init__(self, settings, port):
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.generator = Generator(settings)
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
        application = self.application
        application.settings["log_function"] = lambda x: None
        application.settings["static_handler_class"] = StaticFileHandler
        http_server = tornado.httpserver.HTTPServer(application,
                                                    io_loop=self.ioloop)
        http_server.listen(self.port)
        logger.info("Start server at port %s" % self.port)
        self.ioloop.start()


class PreviewServer(CatsupServer):
    def __init__(self, settings, port):
        super(PreviewServer, self).__init__(settings, port)
        self.generator = Generator(
            settings,
            local=True,
            base_url="http://127.0.0.1:%s/" % port
        )

    @property
    def application(self):
        params = {
            "path": g.output,
            "default_filename": "index.html"
        }
        return tornado.web.Application([
            (r"/(.*)", StaticFileHandler, params),
        ])

    def prepare(self):
        # Reload server when catsup modified.
        tornado.autoreload.start(self.ioloop)
        tornado.autoreload.add_reload_hook(self.generate)

        event_handler = CatsupEventHandler(self.generator)
        observer = Observer()
        for path in [self.generator.config.config.source, g.theme.path]:
            path = os.path.abspath(path)
            observer.schedule(event_handler, path=path, recursive=True)
        observer.start()


class WebhookServer(CatsupServer):
    @property
    def application(self):
        git_path = ""
        for path in ["", self.generator.config.config.source]:
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
