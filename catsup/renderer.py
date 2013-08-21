import os

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from catsup.logger import logger
from catsup.options import g
from catsup.utils import mkdir, static_url, url_for


class Renderer(object):
    def __init__(self, templates_path, generator):
        self.env = Environment(
            loader=FileSystemLoader(templates_path),
            autoescape=False
        )
        config = generator.config
        
        self.env.globals.update(
            generator=generator,
            site=config.site,
            config=config.config,
            author=config.author,
            comment=config.comment,
            theme=config.theme.vars,
            g=g,
            static_url=static_url,
            url_for=url_for
        )

        catsup_filter_path = os.path.join(g.catsup_path, 'filters.py')
        theme_filter_path = os.path.join(g.theme.path, 'filters.py')
        self.load_filters_from_pyfile(catsup_filter_path)
        self.load_filters_from_pyfile(theme_filter_path)

    def load_filters_from_pyfile(self, path):
        if not os.path.exists(path):
            return
        filters = {}
        execfile(path, {}, filters)
        self.env.filters.update(filters)

    def render(self, template, **kwargs):
        try:
            return self.env.get_template(template).render(**kwargs)
        except TemplateNotFound:
            # logger.warning("Template not found: %s" % template)
            pass

    def render_to(self, template, path, **kwargs):
        mkdir(os.path.dirname(path))
        html = self.render(template, **kwargs)
        if html:
            with open(path, "w") as f:
                f.write(html)
