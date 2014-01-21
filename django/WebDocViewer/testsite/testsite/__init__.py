# -*- coding: utf-8 -*-

from __future__ import absolute_import
from django.template import add_to_builtins  
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.


from .celery import app as celery_app
#from  apps.backends.simpletask import simpletask
#simpletask.run()

add_to_builtins('apps.backends.jinja2.jinja_tag')