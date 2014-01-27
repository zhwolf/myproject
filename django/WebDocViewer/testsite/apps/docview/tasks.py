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


@shared_task
def test_add(x, y):
    a = x+y
    logging.info("test_add::%s",a)      
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
    
    session = Session()
    data_db = {}
    try
        dbdatas = session.query(BookSL).filter(
            and_(
              )).all()
        for data in  dbdatas:  
            data_db[data.path] = data
    except Exception,e:
        session.rollback()
        printError() 
        data_db = None
    
    converter = DocConverter(settings.BOOK_BASE, settings.BOOK_OUTPUT_BASE,settings.BASE_DIR, printError)
    data = []
    books = os.walk(settings.BOOK_BASE)
    for path, directory, files in books:
        for filename in files:
            if path == '.':
                continue
            filename =  unicode(filename, DEFAULT_ENCODE)   
            filepath =  unicode(os.path.join(path, filename), DEFAULT_ENCODE)
            data.append(filepath)
            try:
                converter.getswf(filepath)
            except Exception,e:
                printError()                 
                continue
            #sync database
            if data_db == None:
                continue
            item = data_db.get(filepath, None)
            needupdate = False
            if item == None:
                needupdate = True
                print "need add:", filepath
                item = BookSL()
                item.name, item.format = os.path.splitext(os.path.basename(filename))
                item.format = item.format[1:].lower()
                item.uploadtime = datetime.datetime.now()
                item.path = filepath
                item.uploader = ''
                item.bookid =  '%s' % (uuid.uuid1())
                item.cost = 0
                item.bookclass = os.path.basename(filepath).replace('\\', '/')
                item.counter = 0
            else:
                if item.summary == None or item.summary == '':
                    pass  
                    
            if  needupdate:         
                try:
                    session.commit()
                except Exception,e:
                    session.rollback()
                    printError()                 
    print " syncBooks:DONE"    
        
