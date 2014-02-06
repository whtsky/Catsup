# -*- coding:utf-8 -*-

import yaml

from houdini import escape_html
from catsup.reader.utils import not_valid
from catsup.utils import update_nested_dict, ObjectDict


def read_base_meta(path):
    meta = ObjectDict()
    if path:
        pass
    return meta


def parse_meta(lines, path=None):
    lines = [l.strip() for l in lines if l]
    if lines[0].startswith("#"):
        return parse_catsup_meta(lines, path)
    elif lines[0].startswith("---"):
        return parse_yaml_meta(lines, path)
    else:
        not_valid(path)


def parse_yaml_meta(lines, path=None):
    title_line = lines.pop(0)
    if not title_line.startswith("---"):
        not_valid(path)
    meta = read_base_meta(path)
    meta.update(yaml.load("\n".join(lines)))
    return update_nested_dict(ObjectDict(), meta)


def parse_catsup_meta(lines, path=None):
    meta = read_base_meta(path)
    if lines[0][0] == "#":
        meta.title = escape_html(lines.pop(0)[1:].strip())
    for line in lines:
        if not line:
            continue
        if ":" not in line:
            not_valid(path)
        name, value = line.split(':', 1)
        name = name.strip().lstrip('-').strip().lower()
        meta[name] = value.strip()
    return meta
