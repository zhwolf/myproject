#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import web
from jinja2 import Environment,FileSystemLoader

web.config.debug = True

### urls
urls = (
    #'/(.*)/', 'redirect',
#####
    "//*", "index",
    "/edit/*", "edit",
    "/record/*", "record",
    "/history/*", "history",
    )

### global
app = web.application(urls, globals())

def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})
    jinja_env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
        extensions=extensions,
    )
    jinja_env.globals.update(globals)
    #jinja_env.update_template_context(context)
    return jinja_env.get_template(template_name).render(context)

class redirect:
    def GET(self, path):
        web.seeother('/' + path)

class index:
    def GET(self):
        return render_template("index.html")

class edit:
    def GET(self):
        return render_template("edit.html")

class record:
    def GET(self):
        return render_template("record.html")

class history:
    def GET(self):
        return render_template("history.html")

if __name__ == "__main__":
    app.run()
