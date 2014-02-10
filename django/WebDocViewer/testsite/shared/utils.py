# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.conf import settings
import os, sys
from django.core.cache import cache
import logging
import json
import os
import logging
import sys
import traceback
import StringIO
import locale


DEFAULT_ENCODE =  sys.stdin.encoding or locale.getdefaultlocale()[1] or sys.getdefaultencoding()

def sharedContext(request): 
    def walkdir(basedir):
        class Any:
            pass
        result = {
            'label': '',
            'path': '/',
            'children':[
                {
                    'label': u'论文',
                    'path': u'/论文/',
                    'children':[],
                },
                {
                    'label':  u'小说.文学',
                    'path':   u'/小说/',
                    'children':[],
                },
                {
                    'label':  u'管理.面试',
                    'path':   u'/管理/',
                    'children':[],
                },
                {
                    'label':  u'金融.证券',
                    'path':   u'/金融/',
                    'children':[],
                },
                {
                    'label':  u'通信.电子',
                    'path':   u'/通信/',
                    'children':[],
                },
                {
                    'label':  u'考研.英语',
                    'path':   u'/考研/',
                    'children':[],
                },
                {
                    'label':  u'IT.编程',
                    'path':   u'/IT/',
                    'children':[],
                },
            ]
        }    
        helper = result
        '''
        for path, dirs, files in os.walk(basedir):
            name = unicode(os.path.relpath(path, basedir),  DEFAULT_ENCODE)
            if name == ".":
                name = ""
            data = helper.get(name, None)
            if data == None:
                data = Any()
                data.name = name
                data.children = []
                data.father = None
                data.child = []
                
                helper[name] = data
                #root
                result['children'] = data.children
                result['path'] = name.replace('\\', '/')
    
            for cname in dirs:
                cname = unicode(cname, DEFAULT_ENCODE)
                childname = os.path.join(name, cname)
                #print childname
                item = Any()
                helper[childname] = item
                item.name = childname
                item.children = []
                item.father = data
                item.child = []
                data.child.append(item)
                #dic data
                child = {}
                child['label'] = cname
                child['path'] = childname.replace('\\', '/')
                child['children'] = item.children
                
                data.children.append(child)
        '''                
        return json.dumps(result), result, helper
    
    
    def getbookclass():
        if cache.get('bookclass_json', '') == '':
            logging.info('begin to browser classes')
            dirstr, dirdict, dichelper = walkdir(settings.BOOK_BASE)
            cache.set('bookclass_json', dirstr, timeout= None)        
            cache.set('bookclass_dict', dirdict, timeout= None)        
            cache.set('bookclass_helper', dichelper, timeout= None)   
            
    getbookclass()
    s = cache.get('bookclass_json', '')
    return {'menudata': s, }
    
  
        
def printError():
    fp = StringIO.StringIO()
    traceback.print_exc(file=fp)
    ret = fp.getvalue()
    logging.error("exception:%s",ret)        
           