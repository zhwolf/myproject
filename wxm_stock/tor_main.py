#!/usr/bin/env python
# -*- coding: utf-8 -*-

#http://qinxuye.me/article/ways-to-continual-sync-browser-and-server/
import os
import random, time
import logging
import Queue
import re,urllib2
from BeautifulSoup import BeautifulSoup
# import Jinja2
from jinja2 import Environment, FileSystemLoader,TemplateNotFound

# import Tornado
import tornado.ioloop
import tornado.web
import tornado.websocket

settings = {
    'template_path': 'templates',
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    'debug' : True,
    #"cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    #"login_url": "/login",
    "xsrf_cookies": False,
}

### global
# Load template file templates/site.html
class TemplateRendering:
    """
    A simple class to hold methods for rendering templates.
    """
    def render_template(self, template_name, **kwargs):
        template_dirs = ["templates"]
        if self.settings.get('template_path', ''):
            template_dirs.append(
                self.settings["template_path"]
            )

        env = Environment(loader=FileSystemLoader(template_dirs))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content


class BaseHandler(tornado.web.RequestHandler, TemplateRendering):
    """
    RequestHandler already has a `render()` method. I'm writing another
    method `render2()` and keeping the API almost same.
    """
    def render2(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            #'settings': self.settings,
            #'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
            'request': self.request,
            'xsrf_token': self.xsrf_token,
            'xsrf_form_html': self.xsrf_form_html,
        })
        content = self.render_template(template_name, **kwargs)
        self.write(content)




class index(BaseHandler):
    def get(self):
        return self.render2("index.html")

class edit(BaseHandler):
    def get(self):
        return self.render2("edit.html")

class record(BaseHandler):
    def get(self):
        return self.render2("record.html")

class history(BaseHandler):
    def get(self):
        return self.render2("history.html")

class LongPolling(BaseHandler):
    @tornado.web.asynchronous
    def post(self):
        self.num = 0
        self.get_data(callback=self.on_finish)

    def get_data(self, callback):
        if self.request.connection.stream.closed():
            return

        #num = random.randint(1, 100)
        self.num = self.num +1
        tornado.ioloop.IOLoop.instance().add_timeout(
            time.time()+3,
            lambda: callback(self.num)
        ) # 间隔3秒调用回调函数

    def on_finish(self, data):
        self.write("Server says: %d" % data)
        self.finish() # 使用finish方法断开连接

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        for i in xrange(10):
            num = random.randint(1, 100)
            self.write_message(str(num))
            time.sleep(2)

    def on_message(self, message):
        logging.info("getting message %s", message)
        self.write_message("You say:" + message)

    def check_origin(self, origin):
        return True

class StockStatus(tornado.websocket.WebSocketHandler):
    def open(self):
        pass

    def on_message(self, message):
        logging.info("getting message %s", message)
        self.write_message("You say:" + message)

    def check_origin(self, origin):
        return True

    def getStatus(self, stocks):
        def worker():
            while not q.empty():
                item = q.get()


                q.task_done()
            logging.INFO("Thread quit for queue is empty")

        q = Queue.Queue()
        for item in stocks:
            q.put(item)

        for i in range(num_worker_threads):
             t = Thread(target=worker)
             t.daemon = True
             t.start()

        q.join()       # block until all tasks are done



# Assign handler to the server root  (127.0.0.1:PORT/)
application = tornado.web.Application(
    [
    ("//*", index),
    ("/edit/*", edit),
    ("/record/*", record),
    ("/history/*", history),
    ("/LongPolling/*", LongPolling),
    ("/websocket/*", WebSocketHandler),
    ("/stock/status*", StockStatus),
    ],
     **settings)


if __name__ == "__main__":
    application.listen(8080)
    tornado.ioloop.IOLoop.instance().start()
