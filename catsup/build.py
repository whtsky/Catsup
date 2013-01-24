#coding=utf-8
import logging
import os
import copy
import shutil
import time
import hashlib
from tornado.util import ObjectDict
from jinja2 import Environment, FileSystemLoader

from catsup.options import config, g
from catsup.utils import load_posts


def load_filters():
    def static_url(file):

        def get_hash(path):
            path = os.path.join(g.theme.path, 'static', path)
            if not os.path.exists(path):
                logging.warn("%s does not exist." % path)
                return ''

            with open(path, 'r') as f:
                return hashlib.md5(f.read()).hexdigest()[:4]

        hsh = get_hash(file)

        return '%s%s?v=%s' % (config.config["static_prefix"], file, hsh)

    def xmldatetime(t):
        t = time.gmtime(t)
        updated_xml = time.strftime('%Y-%m-%dT%H:%M:%SZ', t)
        return updated_xml

    g.jinja.globals["static_url"] = static_url
    g.jinja.filters["xmldatetime"] = xmldatetime


def load_jinja():
    theme_path = os.path.join(g.theme.path, 'templates')
    g.jinja = Environment(
        loader=FileSystemLoader([theme_path, g.public_templates_path]),
        autoescape=False)

    g.jinja.globals["site"] = ObjectDict(**config.site)
    g.jinja.globals["config"] = ObjectDict(**config.config)
    g.jinja.globals["author"] = config.author
    g.jinja.globals["comment"] = ObjectDict(**config.comment)
    g.jinja.globals["theme"] = ObjectDict(**config.theme["vars"])
    g.jinja.globals["g"] = g

    load_filters()


def write(filename, content):
    filename = os.path.join(config.config["output"], filename)
    with open(filename, 'w') as f:
        f.write(content)


def build_feed():
    logging.info('Generating atom')
    page = g.jinja.get_template('feed.xml').render()
    write('feed.xml', page)


def build_articles():
    logging.info('Start generating articles')
    template = g.jinja.get_template('article.html')
    posts = copy.copy(g.posts)
    posts.reverse()
    prev = None
    post = posts.pop()
    next = len(posts) and posts.pop() or None
    while post:
        logging.info('Generating %s' % post.file_name)
        page = template.render(post=post, prev=prev,
            next=next)
        write('%s.html' % post.file_name, page)
        prev, post, next = post, next, len(posts) and posts.pop() or None


def build_pages():
    logging.info('Start generating index pages')
    template = g.jinja.get_template('index.html')
    p = 0
    posts_num = len(g.posts)

    pages_path = os.path.join(config.config["output"], 'page')

    if os.path.exists(pages_path):
        shutil.rmtree(pages_path)

    os.makedirs(pages_path)

    while posts_num > p * config.config["per_page"]:
        p += 1
        logging.info('Start generating page %s' % p)
        page = template.render(p=p, posts_num=posts_num)
        pager_file = os.path.join('page', "%s.html" % p)
        write(pager_file, page)

    if not g.theme.has_index:
        index_1 = os.path.join(config.config["output"], 'page', '1.html')
        index = os.path.join(config.config["output"], 'index.html')
        os.rename(index_1, index)


def build_tags():
    logging.info('Start generating tag pages')
    template = g.jinja.get_template('tag.html')

    tags_path = os.path.join(config.config["output"], 'tag')

    if os.path.exists(tags_path):
        shutil.rmtree(tags_path)

    os.makedirs(tags_path)

    prev = None
    for i, tag in enumerate(g.tags):
        logging.info('Generating tag %s' % tag.name)
        i += 1
        next = i < len(g.tags) and g.tags[i] or None
        page = template.render(tag=tag, prev=prev,
            next=next)
        tag_file = os.path.join("tag", "%s.html" % tag.name.lower())
        write(tag_file, page)
        prev = tag


def build_archives():
    logging.info('Start generating archive pages')
    template = g.jinja.get_template('archive.html')

    archives_path = os.path.join(config.config["output"], 'archive')

    if os.path.exists(archives_path):
        shutil.rmtree(archives_path)

    os.makedirs(archives_path)

    prev = None
    for i, archive in enumerate(g.archives):
        logging.info('Generating archive %s' % archive.name)
        i += 1
        next = i < len(g.archives) and g.archives[i] or None
        page = template.render(archive=archive, prev=prev,
            next=next)
        archive_file = os.path.join("archive", "%s.html" % archive.name)
        write(archive_file, page)
        prev = archive


def build_others():
    logging.info('Start generating other pages')
    for file in g.theme.pages:
        logging.info('Generating %s' % file)
        template = g.jinja.get_template(file)
        page = template.render()
        write(file, page)


def copy_static():
    logging.info('Copying static files.')

    if os.path.exists(config.config["static"]):
        shutil.rmtree(config.config["static"])

    shutil.copytree(os.path.join(g.theme.path, 'static'),
        config.config["static"])

    favicon = os.path.join(config.config["posts"], 'favicon.ico')
    if not os.path.exists(favicon):
        favicon = os.path.join(g.theme.path, 'static', 'favicon.ico')
    if os.path.exists(favicon):
        shutil.copy(favicon, os.path.join(config.config["output"],
            'favicon.ico'))

    robots = os.path.join(config.config["posts"], 'robots.txt')
    if not os.path.exists(robots):
        robots = os.path.join(g.theme.path, 'static', 'robots.txt')
    if os.path.exists(robots):
        shutil.copy(robots, os.path.join(config.config["output"],
            'robots.txt'))

    logging.info('Done.')


def build():
    load_jinja()
    logging.info('Building your blog..')
    t = time.time()
    load_posts()

    if not g.posts:
        logging.warning("No posts found.Stop building..")
        return

    if os.path.exists(config.config['output']):
        shutil.rmtree(config.config['output'])

    os.makedirs(config.config['output'])

    build_feed()
    build_articles()
    build_pages()
    build_tags()
    build_archives()
    build_others()

    copy_static()

    logging.info('Finish building in %ss' % int(time.time() - t))
