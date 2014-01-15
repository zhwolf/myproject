from __future__ import absolute_import
# -*- coding: utf-8 -*-

from django.conf import settings
from celery import shared_task
import os, sys
import traceback
import StringIO
import logging

from .models import Book


@shared_task
def test_add(x, y):
    return x + y


@shared_task
def test_mul(x, y):
    return x * y


@shared_task
def test_xsum(numbers):
    return sum(numbers)
    
@shared_task
def test_syncBooks():
    from .DocConvert import DocConverter
    converter = DocConverter(settings.BOOK_BASE, settings.BOOK_OUTPUT_BASE,settings.BASE_DIR, printError)
    
    books = os.walk(settings.BOOK_BASE)
    for path, directory, files in books:
        print sys.stdin.encoding
        for filename in files:    
            filepath =  unicode(os.path.join(path, filename), settings.DEFAULT_ENCODE)
            converter.getswf(filepath)
            
    print " syncBooks:DONE"
    
@shared_task
def syncBooks():
    from .DocConvert import DocConverter
    import threadpool
    converter = DocConverter(settings.BOOK_BASE, settings.BOOK_OUTPUT_BASE,settings.BASE_DIR, printError)
    
    data = []
    books = os.walk(settings.BOOK_BASE)
    for path, directory, files in books:
        print sys.stdin.encoding
        for filename in files:    
            filepath =  unicode(os.path.join(path, filename), settings.DEFAULT_ENCODE)
            data.append(filepath)
            #converter.getswf(filepath)
            
    pool = threadpool.ThreadPool(5) 
    requests = threadpool.makeRequests(converter.getswf, data) 
    [pool.putRequest(req) for req in requests] 
    pool.wait()           
    print " syncBooks:DONE"    
        
 
def printError():
    fp = StringIO.StringIO()
    traceback.print_exc(file=fp)
    ret = fp.getvalue()
    logging.error("exception:%s",ret)       