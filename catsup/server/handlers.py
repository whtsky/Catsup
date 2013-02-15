#coding=utf-8
import os
import logging
import tornado.web

import catsup.build
from catsup.options import config


class WebhookHandler(tornado.web.RequestHandler):
    def get(self):
        catsup.build.build()

    def post(self):
        """Webhook support for GitHub and Bitbucket.
        """
        logging.info('Updating posts...')
        current_dir = os.getcwd()
        os.chdir(config.config.source)
        if os.path.isdir('.git'):
            os.system('git pull')
        elif os.path.isdir('.hg'):
            os.system('hg pull')
        else:
            logging.warn("Your post folder is not a git/hg repo folder."
                         "Can not update your posts.")
        os.chdir(current_dir)
        catsup.build.build()
