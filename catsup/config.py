#coding=utf-8
import os.path
from tornado.options import define, options

define('site_title', type=str, default='catsup', help='site title')
define('site_description', type=str, default='a blog', help='site description')
define('site_url', type=str, default='', help='site url')
define("port", type=int, default=8888, help="run on the given port")

define('comment_system', type=str, default='disqus', help='the comment system you use')
define('disqus_shortname', type=str, default='catsup', help='disqus shortname')
define('duoshuo_shortname', type=str, default='catsup', help='duoshuo shortname')

define('static_url', type=str, default='/static', help='static resources url')
define('feed', type=str, default='/feed.xml', help='your rss feed url')

define('theme_name', type=str, default='sealscript', help='the theme you prefer')


define('gzip', type=bool, default=True, help='whether gzip content or not')
define('excerpt_index', type=bool, default=False, help='display excerpt at homepage')
define('date_in_permalink', type=bool, default=True, help='whether permalink contains date or not')
define('post_per_page', type=int, default=3, help='post per page at homepage')

define('twitter', type=str, default='', help='your twitter username')
define('github', type=str, default='', help='your github username')
define('google_analytics', type=str, default='', help='google analytics ID')

define('links', type=tuple, help='your links', default=(
    ('whtsky', 'http://whouz.com', 'I write catsup'),
    ('messense', 'http://messense.me', 'I also write catsup'),
    ('catsup', 'https://github.com/whtsky/catsup', 'the source of this blog'),
))

# catsup system settings, edit it only if you know what you are going to do
define('catsup_path', type=str, default=os.path.dirname(os.path.abspath(__file__)), help='catsup path')
define('posts_path', type=str, default=os.path.join(os.path.dirname(options.catsup_path), '_posts'), help='posts path')
define('common_template_path', type=str, default=os.path.join(options.catsup_path, 'template'), help='common template path')
define('deploy_path', type=str, default=os.path.join(os.path.dirname(options.catsup_path), 'deploy'), help='catsup deploy path')
define('themes_path', type=str, default=os.path.join(options.catsup_path, 'themes'), help='themes path')

define('settings', type=str, default=os.path.join(os.path.expanduser('~'), '.catsuprc'), help='catsup settings file path')

# for catsup use, do not delete them
define('posts', type=list, default=[], help='parsed posts list')
define('tags', type=list, default=[], help='parsed post tags dict')
define('archives', type=list, default=[], help='parsed post archives dict')