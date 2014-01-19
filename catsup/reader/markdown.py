import misaka as m

from houdini import escape_html

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

from catsup.models import Post
from catsup.utils import ObjectDict
from catsup.reader.utils import split_content, parse_meta


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
    meta, content = split_content(path)
    content = content.replace("\n", "  \n")
    if not meta:
        meta = ObjectDict()
    else:
        meta = parse_meta(meta, path)
    return Post(
        path=path,
        meta=meta,
        content=md.render(content)
    )
