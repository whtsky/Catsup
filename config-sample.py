#coding=utf-8
import os
site_title = 'capsule'
site_description = 'a blog'
theme_name = 'sealscript'

catsup_path = os.path.dirname(__file__)
posts_path = os.path.join(catsup_path, '_posts')
theme_path = os.path.join(catsup_path, 'themes', theme_name)

twitter = 'whouz'
github = 'whtsky'
feed = '/feed'

settings = dict(static_path = os.path.join(theme_path, 'static'),
    template_path = os.path.join(theme_path, 'template'),
    gzip = True,
    site_title = site_title,
    site_description = site_description,
    twitter = twitter,
    github = github,
    feed = feed
)
