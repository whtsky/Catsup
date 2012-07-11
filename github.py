#!/usr/bin/env python
import tornado.httpserver
import tornado.web
import tornado.ioloop
import tornado.escape
import os
import config


class ReloadHandler(tornado.web.RequestHandler):
    def post(self):
        if self.request.remote_ip not in config.github_ips:
            pass
        payload = self.get_argument('payload')
        payload = tornado.escape.json_decode(payload)
        if payload['repository']['owner']['name'] != config.github:
            pass
        os.chdir(config.posts_path)
        os.system('git pull')
        os.chdir(config.catsup_path)
        os.system('python catsup-static.py')


application = tornado.web.Application([
    (r'/.*', ReloadHandler),
])

if __name__ == '__main__':
    http_server = tornado.httpserver.HTTPServer(application, xheaders=True)
    http_server.listen(2331)
    tornado.ioloop.IOLoop.instance().start()
