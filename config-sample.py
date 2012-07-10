#coding=utf-8
import os
site_title = 'capsule'
site_description = 'a blog'
site_url = 'https://github.com/whtsky/catsup'
static_url = '/static'
theme_name = 'sealscript'

catsup_path = os.path.dirname(__file__)
posts_path = os.path.join(catsup_path, '_posts')
theme_path = os.path.join(catsup_path, 'themes', theme_name)

twitter = 'whouz'
github = 'whtsky'
feed = '/feed'

links = (
    ('whtsky', 'http://whouz.com', 'I write catsup'),
    ('catsup', 'https://github.com/whtsky/catsup', 'the source of this blog'),
)

github_ips = ('207.97.227.253', '50.57.128.197', '108.171.174.178')
#You can find these ips in your repo's service page.

if site_url.endswith('/'):
    site_url = site_url[:-1]
if static_url.endswith('/'):
    static_url = static_url[:-1]

settings = dict(static_path = os.path.join(theme_path, 'static'),
    template_path = os.path.join(theme_path, 'template'),
    gzip = True,
    site_title = site_title,
    site_description = site_description,
    site_url = site_url,
    twitter = twitter,
    github = github,
    feed = feed,
    links = links,
    static_url = static_url,
)
