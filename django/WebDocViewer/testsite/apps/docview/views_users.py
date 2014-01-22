# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from apps.backends.DBEnginee.djSQLAlchemy import Session,update_model
from sqlalchemy.sql import and_,or_, desc
from .models import Book, UserSL

import datetime
import uuid

import subprocess 
import os
import logging
import sys
import traceback
import StringIO
    

DEFAULT_ENCODE =  sys.stdin.encoding if sys.stdin.encoding else locale.getdefaultlocale()[1] if locale.getdefaultlocale()[1]  else sys.getdefaultencoding()

session = Session()

class Any:
    pass

class UserRegForm(forms.Form):
    account = forms.CharField(label=u'账户名',required = True, max_length=200)
    password = forms.CharField(label=u'密码',required = True, max_length=200)
    password1 = forms.CharField(label=u'确认密码',required = True, max_length=200)
    linkid = forms.CharField(label=u'关联账号',required = True, max_length=200)
        

def printError():
    fp = StringIO.StringIO()
    traceback.print_exc(file=fp)
    ret = fp.getvalue()
    logging.error("exception:%s",ret)

def register(request,regtype):
    error = ""
    regtype = int(regtype) if regtype.isdigit() else 0

    if request.method == 'POST':
        form = UserRegForm(request.POST)
        if regtype !=0:
            form.fields.pop('linkid', None)
        if form.is_valid():
            
                                            
            if form.cleaned_data['password'] != form.cleaned_data['password1']:
                error = u"两次输入密码不一致"
            elif session.query(UserSL).filter(
                                and_(UserSL.account == form.cleaned_data['account'],
                                )).first() != None:
                error = u"该账户已经存在!"                    
            else:                
                try:
                    data = UserSL() 
                    update_model(data, form.cleaned_data)
                    data.userid = '%s' % (uuid.uuid1())
                    data.registertime = datetime.datetime.now()
                    session.add(data)
                    session.commit()
                    info = '保存成功!'
                    return HttpResponseRedirect('/docview/login/')
                except Exception,e:
                    error = u"注册失败.请联系管理员"
                    session.rollback()
                    printError()
        else:
            field, einfo = form.errors.items()[0]
            error = form[field].label +":" +  einfo.as_text()                    
    else:
        form = UserRegForm()
    
    return render(request, 'user/register.html', {'form':form, 'error':error, 'regtype': regtype })    