from __future__ import absolute_import
# -*- coding: utf-8 -*-

from django.conf import settings
import os, sys
import traceback
import StringIO
import logging
import Queue
import threadpool
import uuid
import threading
import datetime
import time
import importlib 

_dispatchQueue = Queue.Queue()
_scheduleQueue = []
_dispatchpool = threadpool.ThreadPool(5) 
_schedulepool = threadpool.ThreadPool(2) 

SIMPLETASK_SCHEDULE = {}

def test_add(x,y):
    print x
    print y
    a = x+y
    logging.debug( "add:%s", a)
        
class AsyncTask:
    def __init__(self,func, args, kwargs):
        self.id = '%s' % (uuid.uuid1())
        self.func = func
        self.args = args
        self.kwargs = kwargs
        
class ScheduleTask:
    def __init__(self,func,interval, args, kwargs):
        self.id = '%s' % (uuid.uuid1())
        self.interval = interval
        self.func = func
        self.args = args
        self.kwargs = kwargs        
        self.lasttime = datetime.datetime.now() -interval

def pushtask(func, *args, **kwargs):
    task = AsyncTask(func, args, kwargs)
    _dispatchQueue.put( task )
    logging.debug("get a task:%s", task.id)
    return task.id
    
def canceltasks():
    while True:
        try:
            timeout = 0.01
            _dispatchQueue.get(block = True, timeout = timeout)
        except Exception,e:
            break   
            
def scheduletask(func, interval, *args, **kwargs):
    task = ScheduleTask(func, interval, args, kwargs)
    _scheduleQueue.append( task )
    logging.debug("get a schedule task:%s", task.id)
    return task.id
            
        
def run():
    def dispatcher():
        logging.debug("dispatcher...")
        while True:
            jobs = []
            while True:
                try:
                    timeout = 1
                    if len(jobs) > 0:
                        timeout = 0.01
                    task = _dispatchQueue.get(block = True, timeout = timeout)
                    jobs.append( task )
                except Exception,e:
                    break     
                    
            if len(jobs) > 0:                    
                for task in jobs:        
                    _dispatchpool.putRequest( threadpool.WorkRequest(task.func, task.args, task.kwargs ) )
                    logging.debug("process %s... ", task.id)
                _dispatchpool.wait() 
                logging.debug("dispatcher DONE")
                  
    def scheduler():       
        SIMPLETASK_SCHEDULE = getattr(settings, 'SIMPLETASK_SCHEDULE', {})
        logging.debug("scheduler...%s", SIMPLETASK_SCHEDULE.items())
        for name, item in SIMPLETASK_SCHEDULE.items():
            modfunc = item.get('task', '').strip()
            if modfunc == '':
                logging.error("schedule job:%s is illegl", name)    
                continue
            interval = item.get('interval', None)
            if interval == None or not isinstance(interval, datetime.timedelta) :
                logging.error("schedule job:%s interval is illegl", name)    
                continue
            args = item.get('args', None)
                
            i = modfunc.rfind('.') 
            modname = ''
            if i >=0:
                modname = modfunc[:i]
                funcname = modfunc[i+1:]
            else:
                funcname = modfunc    
            try:
                print modname, funcname
                if modname != '':
                    obj = importlib.import_module(modname)
                    #obj = sys.modules[modname]
                    func = getattr(obj, funcname)
                else:
                    func = eval(funcname)
                print func                    
                logging.info("imported:%s %s-%s", modfunc, modname, func)                    
                scheduletask(  func,  interval, *args)                 
            except Exception,e:
                logging.error("Load %s, exception:%s", modfunc,e)                    
                continue                
            
        while True:
            jobs = []
            now = datetime.datetime.now()
            count = 0
            for task in _scheduleQueue:
                if now - task.lasttime >= task.interval: 
                    _schedulepool.putRequest( threadpool.WorkRequest(task.func, task.args, task.kwargs ) )
                    task.lasttime = now
                    logging.debug("process %s... ", task.id)       
                    count +=1
            if count > 0:                    
                _schedulepool.wait()
                logging.debug("scheduler DONE")
            time.sleep(0.5)                
       
        
    a = threading.Thread(target = dispatcher)
    a.daemon = True    
    a.start()         
    
    b = threading.Thread(target = scheduler)
    b.daemon = True    
    b.start()  
    
    print "gogogo"   
