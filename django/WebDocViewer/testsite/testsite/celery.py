# -*- coding: utf-8 -*-

from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
import threading

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testsite.settings')

app = Celery('testsite')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
    
    
print "Into celery"    
import socket
import subprocess 
from djcelery.management.commands import celery
import time

def worker():
    return
    args = ['manage.py', 'celery', 'worker', '-lINFO']
    command = celery.Command()
    command.run_from_argv(args)
    pass
    
def shcedule():
    return
    args = ['manage.py', 'celery', 'beat', '-lINFO']
    command = celery.Command()
    command.run_from_argv(args)
    pass    
    

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('127.0.0.1', 2531))
    print "I am under singleton now"
    a = threading.Thread(target = worker)
    a.daemon = True

    b = threading.Thread(target = shcedule)
    b.daemon = True
    
    b.start()
    time.sleep(2)
    a.start()
except Exception,e:
    pass    