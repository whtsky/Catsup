#!/usr/bin/env python
#coding=utf-8
from __future__ import print_function

from catsup import *

import tornado.template
import sys
import shutil


deploy_dir = 'deploy'
if len(sys.argv) > 1:
    deploy_dir = sys.argv[1]
deploy_dir = os.path.join(config.catsup_path, deploy_dir)


if __name__ == '__main__':
    shutil.rmtree(deploy_dir)
    os.makedirs(deploy_dir)
    print('Start generating articles')
    loader = tornado.template.Loader(config.settings['template_path'],
        autoescape=None)
    generator = loader.load("article.html")
    for i in range(posts_num):
        post = posts[i]
        prev = next = None
        print('Generating %s' % post['file_name'])
        if i:#i>0
            prev = posts[i-1]
        if (i+1) < posts_num:
            next = posts[i+1]
        page = generator.generate(post=post, handler=config,
            prev=prev, next=next)
        file_path = os.path.join(deploy_dir, '%s.html' % post['file_name'])
        open(file_path, 'w').write(page)

    print('Start generating atom')
    page = loader.load("feed.xml").generate(posts=posts[:5], handler=config)
    file_path = os.path.join(deploy_dir, 'feed.xml')
    open(file_path, 'w').write(page)

    print('Start generating index pages..')
    generator = loader.load("index.html")
    p = 0
    while posts_num > (p*3):
        p += 1
        print('Start generating page %s' % p)
        page = generator.generate(posts=posts, handler=config,
        p=p)
        file_path = os.path.join(deploy_dir, 'page_%s.html' % p)
        open(file_path, 'w').write(page)

    index_1 = os.path.join(deploy_dir, 'page_1.html')
    index = os.path.join(deploy_dir, 'index.html')
    os.rename(index_1, index)

    print('Copying static files.')
    deploy_static_dir = os.path.join(deploy_dir, 'static')
    shutil.copytree(config.settings['static_path'], deploy_static_dir)

    print('Done.')