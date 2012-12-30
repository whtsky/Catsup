#-* coding:utf-8 -*-
from tornado.web import UIModule
from tornado.options import options

class CommentModule(UIModule):
    def render(self, tpl="%s/comment.html" % options.ui_modules_path):
        return self.render(tpl)

ui_modules = {
    'CommentModule' : CommentModule,
}