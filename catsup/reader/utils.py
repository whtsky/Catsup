import re

from catsup.options import config

html_re = re.compile('(<.*?>)')
summary_re = re.compile('(<h[\d]+>.*?)<h[\d]+>', re.S)


def get_summary(post):
    if not config.config.display_summary:
        post.has_more = False
        return post.content
    post.has_more = True
    if '<!--more-->' in post.source:
        summary = post.source.split('<!--more-->')[0]
        return post.render(summary)
    elif '<hr/>' in post.content:
        return post.content.split('<hr/>')[0]
    elif '<h' in post.content:
        summary = summary_re.findall(post.content)
        if summary:
            return summary[0]
    else:
        #TAT
        post.has_more = False
        return post.content


def get_description(post):
    return html_re.sub('', post.summary)[:195].replace('\n', ' ')
