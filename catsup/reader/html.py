from houdini import escape_html

from catsup.models import Post
from catsup.utils import ObjectDict, to_unicode
from catsup.reader.utils import open_file, not_valid


def parse_meta(lines, path=None):
    lines = [l.strip() for l in lines if l]
    if lines[0].startswith("#"):
        return parse_catsup_meta(lines, path)
    elif lines[0].startswith("---"):
        return parse_liquid_meta(lines, path)
    else:
        not_valid(path)


def parse_liquid_meta(lines, path=None):
    meta = ObjectDict()
    return meta


def parse_catsup_meta(lines, path=None):
    meta = ObjectDict()
    title_line = lines.pop(0)
    if title_line[0] != "#":
        not_valid(path)
    meta.title = escape_html(title_line[1:].strip())
    for line in lines:
        if not line:
            continue
        if ":" not in line:
            not_valid(path)
        name, value = line.split(':', 1)
        name = name.strip().lstrip('-').strip().lower()
        meta[name] = value.strip()
    return meta


def html_reader(path):
    post_file = open_file(path)

    lines = []
    firstline = post_file.readline().strip()

    no_meta = False

    lines.append(firstline)
    for l in post_file:
        l = l.strip()
        if l.startswith("---"):
            break
        elif l:
            lines.append(l)
    else:
        no_meta = True
    if no_meta:
        import os

        p, _ = os.path.splitext(path)
        filename = os.path.basename(p)
        meta = ObjectDict(
            title=filename
        )
        content = "\n".join(lines)
    else:
        meta = parse_meta(lines, path)
        content = "".join(post_file)
    return Post(
        path=path,
        meta=meta,
        content=to_unicode(content)
    )
