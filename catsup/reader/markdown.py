import misaka as m

from houdini import escape_html
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from catsup.logger import logger
from catsup.generator.models import Post
from catsup.utils import to_unicode, ObjectDict


class CatsupRender(m.HtmlRenderer, m.SmartyPants):
    def block_code(self, text, lang):
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except ClassNotFound:
            text = escape_html(text.strip())
            return '\n<pre><code>%s</code></pre>\n' % text
        else:
            formatter = HtmlFormatter()
            return highlight(text, lexer, formatter)

    def autolink(self, link, is_email):
        if is_email:
            s = '<a href="mailto:{link}">{link}</a>'
        elif link.endswith(('.jpg', '.png', '.git', '.jpeg')):
            s = '<a href="{link}"><img src="{link}" /></a>'
        else:
            s = '<a href="{link}">{link}</a>'
        return s.format(link=link)

md = m.Markdown(CatsupRender(flags=m.HTML_USE_XHTML),
                extensions=m.EXT_FENCED_CODE |
                m.EXT_NO_INTRA_EMPHASIS |
                m.EXT_AUTOLINK |
                m.EXT_STRIKETHROUGH |
                m.EXT_SUPERSCRIPT)


def markdown_reader(path):
    meta = ObjectDict()

    try:
        with open(path, "r") as f:
            lines = f.readlines()
    except IOError:
        logger.error("Can't open file %s" % path)
        exit(1)

    def invailed_post():
        logger.error("%s is not a vailed catsup post" % self.filename)
        exit(1)

    title = lines.pop(0)
    if title.startswith("#"):
        meta["title"] = escape_html(title[1:].strip())
    else:
        invailed_post()

    for i, line in enumerate(lines):
        if ':' in line:  # property
            name, value = line.split(':', 1)
            name = name.strip().lstrip('-').strip().lower()
            meta[name] = value.strip()

        elif line.strip().startswith('---'):
            content = md.render(
                to_unicode('\n'.join(lines[i + 1:]))
            )

            return Post(
                path=path,
                meta=meta,
                content=content
            )

    invailed_post()

