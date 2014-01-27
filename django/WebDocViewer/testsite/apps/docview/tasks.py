from __future__ import absolute_import
# -*- coding: utf-8 -*-

from django.conf import settings
from celery import shared_task
import os, sys
import traceback
import StringIO
import logging
from shared.utils import printError, DEFAULT_ENCODE
import datetime,os
import uuid
import time


@shared_task
def test_add(x, y):
    a = x+y
    logging.info("test_add::%s",a)      
    time.sleep(10)
    return x + y


@shared_task
def test_mul(x, y):
    return x * y


@shared_task
def test_xsum(numbers):
    return sum(numbers)
    
@shared_task
def syncBatchBooks(paths):
    from .DocConvert import DocConverter
    print "syncBatchBooks", paths
    converter = DocConverter(settings.BOOK_BASE, settings.BOOK_OUTPUT_BASE,settings.BASE_DIR, printError)
    
    if isinstance(paths, str) or isinstance(paths, unicode):
        converter.getswf(paths)
    else:
        for path in paths:
            converter.getswf(path)
    print " syncBatchBooks:DONE"
    
@shared_task
def syncBooks():
    from .DocConvert import DocConverter
    from .models import BookSL
    from apps.backends.DBEnginee.djSQLAlchemy import Session
    from sqlalchemy.sql import and_,or_, desc

    session = Session()
    data_db = {}
    try:
        dbdatas = session.query(BookSL).filter(
            and_(
              )).all()
        for data1 in  dbdatas:  
            data_db[data1.path] = data1
    except Exception,e:
        session.rollback()
        printError() 
        data_db = None
    
    converter = DocConverter(settings.BOOK_BASE, settings.BOOK_OUTPUT_BASE,settings.BASE_DIR, printError)
    data = []
    books = os.walk(settings.BOOK_BASE)
    for path, directory, files in books:
        if not isinstance(path, unicode)  :
            path =  unicode(path, DEFAULT_ENCODE)   
            
        relpath = os.path.relpath(path, settings.BOOK_BASE)
        if  relpath == '.':
            continue
        
        for filename in files:
            print  path, filename   
            if not isinstance(filename, unicode)  :
                filename =  unicode(filename, DEFAULT_ENCODE)   
            filepath =  os.path.join(path, filename)
            if not isinstance(filepath, unicode)  :
                filepath = unicode(filepath, DEFAULT_ENCODE)
            data.append(filepath)
            
            try:
                converter.getswf(filepath)
            except Exception,e:
                printError()                 
                continue
            #sync database
            if data_db == None:
                continue
            item = data_db.get( os.path.join(relpath,filename) , None)
            needupdate = False
            if item == None:
                needupdate = True
                print "need add:", filepath
                item = BookSL()
                session.add(item)
                item.name, item.format = os.path.splitext(os.path.basename(filename))
                item.format = item.format[1:].lower()
                item.uploadtime = datetime.datetime.now()
                item.path = filepath
                item.uploader = ''
                item.bookid =  '%s' % (uuid.uuid1())
                item.cost = 0
                item.bookclass = os.path.basename(filepath).replace('\\', '/')
                item.counter = 0
            if item.summary == None or item.summary == '':
                item.summary=  testsum(converter.gettxt(filepath))
                needupdate = True
                
                    
            if  needupdate:         
                try:
                    session.commit()
                except Exception,e:
                    session.rollback()
                    printError()         
    from haystack.management.commands import update_index
    args = ['manage.py', '']
    command = update_index.Command()
    command.run_from_argv(args)
                                
    print " syncBooks:DONE"    


def testsum(filename):  
    f = open(  filename)
    txt = ""
    for line in f.readlines():
        try:
            txt += line.decode('utf-8','ignore').encode(DEFAULT_ENCODE).strip()
        except:
            printError()  
            pass            
        if len(txt) >= 3000:
            break
    f.close()
    
    print txt[:10]
    from yaha.analyse import *
    return summarize3( txt)        
