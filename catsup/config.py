#coding=utf-8
from __future__ import with_statement
import sys
import ConfigParser
import os.path
from tornado.options import define, options

# configuration sections
_sections = {
    'site': ('site_title', 'site_url', 'site_description',
             'static_url', 'port', 'feed'),
    'comment': ('comment_system', 'duoshuo_shortname',
                'disqus_shortname'),
    'post': ('date_in_permalink', 'excerpt_index',
             'post_per_page'),
    'theme': ('theme_name', ),
    'sns': ('twitter', 'github'),
    'system': ('posts_path', 'build_path', 'themes_path'),
    'other': ('google_analytics', ),
}


def init():
    """ Provide this function for stopping complain of import-but-unused """
    define('site_title', type=str,
           default='catsup', help='site title')
    define('site_description', type=str,
           default='a blog', help='site description')
    define('site_url', type=str,
           default='', help='site url')
    define("port", type=int,
           default=8888, help="run on the given port")
    define('static_url', type=str,
           default='/static', help='static resources url')
    define('feed', type=str,
           default='/feed.xml', help='your rss feed url')

    define('comment_system', type=str,
           default='disqus', help='the comment system you use')
    define('disqus_shortname', type=str,
           default='catsup', help='disqus shortname')
    define('duoshuo_shortname', type=str,
           default='catsup', help='duoshuo shortname')

    define('theme_name', type=str,
           default='sealscript', help='the theme you prefer')

    define('excerpt_index', type=bool,
           default=False, help='display excerpt at homepage')
    define('date_in_permalink', type=bool,
           default=True, help='whether permalink contains date or not')
    define('post_per_page', type=int,
           default=3, help='post per page at homepage')

    define('twitter', type=str,
           default='', help='your twitter username')
    define('github', type=str,
           default='', help='your github username')
    
    define('google_analytics', type=str,
           default='', help='google analytics ID')

    define('links', type=tuple, help='your links', default=(
        ('whtsky', 'http://whouz.com', 'I write catsup'),
        ('messense', 'http://messense.me', 'I also write catsup'),
        ('catsup', 'https://github.com/whtsky/catsup', 'the source of this blog'),
    ))

    # catsup system settings, edit it only if you know what you are going to do
    define('catsup_path', type=str,
           default=os.path.dirname(os.path.abspath(__file__)), help='catsup path')
    define('posts_path', type=str,
           default=os.path.join(os.path.expanduser('~'), 'posts'), help='posts path')
    define('common_template_path', type=str,
           default=os.path.join(options.catsup_path, 'template'), help='common template path')
    define('global_themes_path', type=str,
           default=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'themes'),
           help='global themes path')
    define('build_path', type=str,
           default=os.path.join(os.getcwd(), 'build'), help='catsup build path')
    define('themes_path', type=str,
           default=os.path.join(options.catsup_path, 'themes'), help='themes path')
    define('settings', type=str,
           default=os.path.join(os.getcwd(), 'config.ini'), help='catsup settings file path')

    # for catsup use, do not delete them
    define('posts', type=list,
           default=[], help='parsed posts list')
    define('tags', type=list,
           default=[], help='parsed post tags list')
    define('archives', type=list,
           default=[], help='parsed post archives list')
    define('config_loaded', type=bool,
           default=False, help='mark config loaded or not')


def parse_config_file(path):
    """
    Parser .ini configuration file
    """
    if path and os.path.exists(path):
        print('Parsing settings file %s' % path)
        parser = ConfigParser.SafeConfigParser()
        with open(path, 'r') as fp:
            parser.readfp(fp)
            for sec in _sections:
                keys = _sections[sec]
                for key in keys:
                    value = parser.get(sec, key)
                    if value in ('Yes', 'On'):
                        value = True
                    elif value in ('No', 'Off'):
                        value = False
                    if key in options:
                        if options[key].type:
                            options[key].set(options[key].type(value))
                        else:
                            options[key].set(value)
                    else:
                        define(key, value)
        options.config_loaded = True
    # execute the codes below no matter whether config file exists or not
    if 'theme_path' not in options:
        theme_path = os.path.join(options.themes_path, options.theme_name)
        if not os.path.isdir(theme_path):
            theme_path = os.path.join(options.global_themes_path, options.theme_name)
        if not os.path.isdir(theme_path):
            print("Theme %s does not exists. Catsup failed to start." % options.theme_name)
            sys.exit(0)
        define('theme_path', theme_path)
    if 'template_path' not in options:
        define('template_path', os.path.join(options.theme_path, 'template'))
    if 'static_path' not in options:
        define('static_path', os.path.join(options.theme_path, 'static'))
    if options.site_url.endswith('/'):
        options.site_url = options.site_url[:-1]
    if options.static_url.endswith('/'):
        options.static_url = options.static_url[:-1]
    if not (options.site_url == ''
            or options.site_url.startswith('http://')
            or options.site_url.startswith('https://')
            or options.site_url.startswith('//')):
        options.site_url = "//%s" % options.site_url


def save_config_file(path):
    """
    Save options into .ini configuration file
    """
    parser = ConfigParser.SafeConfigParser()
    for sec in _sections:
        parser.add_section(sec)
        keys = _sections[sec]
        for key in keys:
            if key in options:
                value = options[key].value()
                if value is bool:
                    if value:
                        value = 'Yes'
                    else:
                        value = 'No'
                if not value is str:
                    value = str(value)
                parser.set(sec, key, value)
    with open(path, 'w') as fp:
        parser.write(fp)
