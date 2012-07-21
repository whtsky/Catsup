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

posts_num = len(posts)
config.settings['tags'] = tags


def write(file_name, page):
    file_path = os.path.join(deploy_dir, file_name)
    open(file_path, 'w').write(page)

if __name__ == '__main__':
    if not os.path.exists(deploy_dir):
        os.makedirs(deploy_dir)

    loader = tornado.template.Loader(config.common_template_path,
        autoescape=None)

    print('Start generating sitemap')
    page = loader.load("sitemap.txt").generate(posts=posts, handler=config)
    write('sitemap.txt', page)

    print('Start generating atom')
    page = loader.load("feed.xml").generate(posts=posts, handler=config)
    write('feed.xml', page)

    loader = tornado.template.Loader(config.settings['template_path'],
        autoescape=None)

    print('Start generating index pages')
    generator = loader.load("index.html")
    p = 0
    while posts_num > p * 3:
        p += 1
        print('Start generating page %s' % p)
        page = generator.generate(posts=posts, handler=config,
            p=p)
        write('page_%s.html' % p, page)

    index_1 = os.path.join(deploy_dir, 'page_1.html')
    index = os.path.join(deploy_dir, 'index.html')
    os.rename(index_1, index)

    print('Start generating index tags')
    generator = loader.load("tag.html")
    for tag in tags:
        print('Start generating tag %s' % tag[0])
        page = generator.generate(tag=tag, handler=config)
        write('tag_%s.html' % tag[0], page)

    print('Start generating articles')
    generator = loader.load("article.html")
    posts.reverse()

    prev = None
    post = posts.pop()
    next = len(posts) and posts.pop() or None
    while post:
        print('Generating %s' % post['file_name'])
        page = generator.generate(post=post, handler=config,
            prev=prev, next=next)
        write('%s.html' % post['file_name'], page)
        prev, post, next = post, next, len(posts) and posts.pop() or None

    print('Start generating 404 page')
    page = loader.load("404.html").generate(handler=config)
    write('404.html', page)

    print('Copying static files.')
    deploy_static_dir = os.path.join(deploy_dir, 'static')
    if os.path.exists(deploy_static_dir):
        shutil.rmtree(deploy_static_dir)
    shutil.copytree(config.settings['static_path'], deploy_static_dir)

    print('Done.')
