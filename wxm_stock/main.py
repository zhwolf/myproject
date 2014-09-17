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
    "^//*", "index",
    "^/edit/*", "edit",
    "^/edit/stock/(\d+)/*", "UpdateStock",
    "^/record/*", "record",
    "^/history/*", "history",
    )

### global
app = web.application(urls, globals())
db = web.database(dbn = "sqlite",
                  db = "./stock.dat")

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

class UpdateStock:
    def GET(self, code):
        data = None
        try:
            code = int(code.strip())
        except:
            code = 0
        if code != 0:
            myvar = dict(code=code)
            datas = db.select('stocks', myvar, where="id=  $code", limit=1)
            for data in datas:
                break
        return render_template("updateStock.html", data=data)

    def POST(self, code):
        try:
            code = int(code.strip())
        except:
            code = 0
        if code != 0:
            myvar = dict(code=code)
            datas = db.select('stocks', myvar, where="id=  $code", limit=1)
            for data in datas:
                break

        data = web.data() # you can get data use this method

class record:
    def GET(self):
        return render_template("record.html")

class history:
    def GET(self):
        return render_template("history.html")

if __name__ == "__main__":
    app.run()
