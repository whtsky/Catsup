import os

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from catsup.options import g
from catsup.utils import mkdir, static_url, url_for, urljoin


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
            pages=generator.pages,
            static_url=static_url,
            url_for=url_for
        )

        catsup_filter_path = os.path.join(
            g.catsup_path, "templates", 'filters.py'
        )
        theme_filter_path = os.path.join(g.theme.path, 'filters.py')
        self.load_filters_from_pyfile(catsup_filter_path)
        self.load_filters_from_pyfile(theme_filter_path)
        self.rendered_permalinks = []

    def load_filters_from_pyfile(self, path):
        if not os.path.exists(path):
            return
        filters = {}
        exec(open(path).read(), {}, filters)
        self.env.filters.update(filters)

    def render(self, template, **kwargs):
        try:
            return self.env.get_template(template).render(**kwargs)
        except TemplateNotFound:
            # logger.warning("Template not found: %s" % template)
            pass

    def render_to(self, template, permalink, **kwargs):
        html = self.render(template, **kwargs)
        if not html:
            return
        permalink, output_name = urljoin(
            g.base_url,
            permalink
        ), permalink
        kwargs.setdefault("permalink", permalink)
        self.rendered_permalinks.append(permalink)
        if output_name.endswith("/") or "." not in output_name:
            output_name = output_name.rstrip("/")
            output_name += '/index.html'
        output_path = os.path.join(g.output, output_name.lstrip("/"))
        mkdir(os.path.dirname(output_path))
        with open(output_path, "w") as f:
            f.write(html)

    def render_sitemap(self):
        with open(os.path.join(g.output, "sitemap.txt"), "w") as f:
            f.write("\n".join(self.rendered_permalinks))
