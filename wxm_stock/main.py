#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import web
from jinja2 import Environment,FileSystemLoader
import utils
web.config.debug = True

### urls
urls = (
    #'/(.*)/', 'redirect',
#####
    "^//*", "index",
    "^/edit/*", "edit",
    "^/edit/stock/(.*)/edit/*", "UpdateStock",
    "^/edit/stock/(.*)/del/*", "RemoveStock",
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

    def POST(self):
        inputs = web.input()
        wheres = {}
        a = inputs.get('query_code', '')
        if  a!= '':
            wheres['stocks.code'] = a
        else:
            a = inputs.get('query_zone', '')
            if a !='':
                wheres['stocks.zone'] = a
            a = inputs.get('query_industry', '')
            if a !='':
                wheres['stocks.industry'] = a
            a = inputs.get('query_subindustry', '')
            if a !='':
                wheres['stocks.subindustry'] = a
        datas = db.where('stocks', limit=100, **wheres)

        return render_template("edit.html", datas=datas)

class RemoveStock:
    def GET(self, code):
        code = code.strip()
        if code != "":
            db.delete('stocks', where="code=  $code",vars ={'code':code})
        return web.seeother("/edit/")

class UpdateStock:
    def GET(self, code):
        data = None
        code = code.strip()
        if code != "":
            datas = db.select('stocks', where="code=  $code",vars ={'code':code}, limit=1)
            for data in datas:
                break
        return render_template("updateStock.html", data=data, queryurl="/edit/")

    def POST(self, code):
        inputs = web.input()
        id = inputs.get('id', '')
        try:
            id = int(id)
        except:
            id = 0
        errs = ""
        count = int(db.query("SELECT count(id) as stocks_total FROM stocks WHERE id !=$id and code= $code", vars={'id':id, 'code': inputs.get('code', '')})[0].stocks_total)
        result = count ==0
        if result:
            myvars ={}
            for field in utils.Table_Stocks:
                if inputs.has_key(field):
                    myvars[field] =inputs.get(field)
            try:
                if id <=0:
                    db.insert('stocks', **myvars)
                else:
                    db.update('stocks', "id = $id", {'id':id},  **myvars)
                result = True
            except Exception as e:
                result = False
                errs = u"数据库错误!"
        else:
            errs = u"已经存在相同的股票代码!"
        if result:
            return web.seeother("/edit/")
        else:
            return render_template("updateStock.html", data=inputs, errs = errs, queryurl="/edit/")



class record:
    def GET(self):
        return render_template("record.html")

class history:
    def GET(self):
        return render_template("history.html")

if __name__ == "__main__":
    app.run()
