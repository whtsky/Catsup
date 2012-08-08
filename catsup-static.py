#!/usr/bin/env python
#coding=utf-8
from __future__ import print_function

from catsup import *

import tornado.template
import os
import sys
import shutil


deploy_dir = 'deploy'
if len(sys.argv) > 1:
    deploy_dir = sys.argv[1]
deploy_dir = os.path.join(config.catsup_path, deploy_dir)

posts_num = len(posts)
config.settings['tags'] = tags
config.settings['archives'] = archives


def write(file_name, page):
    file_path = os.path.join(deploy_dir, file_name)
    open(file_path, 'w').write(page)


def generate():
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)

    os.makedirs(deploy_dir)

    loader = tornado.template.Loader(config.common_template_path,
        autoescape=None)

    print('Generating sitemap')
    page = loader.load("sitemap.txt").generate(posts=posts, handler=config,
        tags=tags, archives=archives)
    write('sitemap.txt', page)

    print('Generating atom')
    page = loader.load("feed.xml").generate(posts=posts, handler=config)
    write('feed.xml', page)

    loader = tornado.template.Loader(config.settings['template_path'],
        autoescape=None)

    print('Start generating index pages')
    generator = loader.load("index.html")
    p = 0
    while posts_num > p * config.settings['post_per_page']:
        p += 1
        print('Start generating page %s' % p)
        page = generator.generate(posts=posts, handler=config,
            p=p)
        write('page_%s.html' % p, page)

    index_1 = os.path.join(deploy_dir, 'page_1.html')
    index = os.path.join(deploy_dir, 'index.html')
    os.rename(index_1, index)

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

    print('Start generating tag pages')
    generator = loader.load("tag.html")
    prev = None
    for i, tag in enumerate(tags):
        print('Generating tag %s' % tag[0])
        i += 1
        next = i < len(tags) and tags[i] or None
        page = generator.generate(tag=tag, prev=prev,
            next=next, handler=config)
        write('tag_%s.html' % tag[0], page)
        prev = tag

    print('Start generating archive pages')
    generator = loader.load("archive.html")
    prev = None
    for i, archive in enumerate(archives):
        print('Generating archive %s' % archive[0])
        i += 1
        next = i < len(archives) and archives[i] or None
        page = generator.generate(archive=archive, prev=prev,
            next=next, handler=config)
        write('archive_%s.html' % archive[0], page)
        prev = archive

    print('Start generating other pages')
    for p in ('404', 'tags', 'archives', 'links'):
        page = loader.load("%s.html" % p).generate(handler=config)
        write('%s.html' % p, page)

    print('Copying static files.')
    deploy_static_dir = os.path.join(deploy_dir, 'static')
    if os.path.exists(deploy_static_dir):
        shutil.rmtree(deploy_static_dir)
    shutil.copytree(config.settings['static_path'], deploy_static_dir)
    os.chdir(deploy_dir)
    os.system('cp static/favicon.ico ./')
    os.system('cp static/robots.txt ./')

    print('Done.')

if __name__ == '__main__':
    generate()
