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
from .models import BookSL, UserSL,UserBookSL
from django.template import RequestContext

from shared.utils import printError, DEFAULT_ENCODE
import json

import datetime
import uuid

import subprocess 
import os
import logging
    

session = Session()

class Any:
    pass

class UserRegForm(forms.Form):
    account = forms.CharField(label=u'账户名',required = True, max_length=200)
    password = forms.CharField(label=u'密码',required = True, max_length=200)
    password1 = forms.CharField(label=u'确认密码',required = True, max_length=200)
    linkid = forms.CharField(label=u'关联账号',required = True, max_length=200)
        
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
        

def addfavorite(request,bookid):
    result = {}
    
    userid= request.session.get('userkey', '')
    
    if userid == '':
        result['code'] = -1
        result['msg'] =  u'请先登陆,才能试用该功能'
    else:
        if session.query(UserBookSL).filter(
                                    and_(
                                        UserBookSL.userid == userid,
                                        UserBookSL.bookid == bookid,
                                    )).first() == None:       
                                                
            try:
                data = UserBookSL() 
                data.userid = userid
                data.bookid = bookid
                data.bindtime = datetime.datetime.now()
                data.flag = 0

                session.add(data)
                session.commit()

                result['code'] = 1
                result['msg'] =  u'收藏成功'

            except Exception,e:
                error = u"注册失败.请联系管理员"
                session.rollback()
                printError()
                result['code'] = -2
                result['msg'] =  u'服务器内部错误，请联系管理员'
        else:
            result['code'] = 1
            result['msg'] =  u'已收藏'
            
    s = json.dumps(result)
    print s
    return HttpResponse(s)
        
def myfavorite(request):
    try:
        data = session.query(BookSL, UserBookSL).filter(
            and_(
                BookSL.bookid == UserBookSL.bookid, 
                UserBookSL.userid == request.session.get('userkey', '')
              ))
    except Exception,e:
        session.rollback()
        printError()        
    return render_to_response('user/myfavorite.html', {'data' : data, }, context_instance=RequestContext(request) )   
        
def removefavorite(request, id):
    try:
        data = session.query(UserBookSL).filter(
            and_(
                UserBookSL.id == id,
              )).first()
        session.delete(data)
        session.commit()      
    except Exception,e:
        session.rollback()
        printError()        
    return HttpResponseRedirect('/docview/user/myfavorite/' )   
           