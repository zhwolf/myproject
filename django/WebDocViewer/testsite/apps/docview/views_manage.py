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
from .models import Book, BookSL, UserSL
from .tasks import syncBatchBooks
from shared.utils import printError, DEFAULT_ENCODE

from .DocConvert import DocConverter
import datetime
import uuid

import subprocess 
import os
import logging
import jieba
    


from haystack.forms import SearchForm, ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Exact, Clean
from haystack.views import SearchView, search_view_factory


session = Session()

class Any:
    pass

class ListSearchForm(forms.Form):
    search = forms.CharField(label=u'查找',required = False, max_length=200)
      
        
class UploadFileForm(forms.Form):
    bookclass = forms.CharField(label=u'文档分类',required = True, max_length=200)
    author = forms.CharField(label=u'作者',required = False, max_length=200)
    tags = forms.CharField(label=u'关键字',required = False,  max_length=200)
    descr = forms.CharField(label=u'简介',required = False,  max_length=1024)
    name = forms.CharField(label=u'名称',required = False,  max_length=200)
    cost = forms.IntegerField(label=u'价值',required = True,)
    file = forms.FileField(label=u'上传',required = True, error_messages = {
           'required': u'请选择文件.',
        }, )
        
class UserInfoForm(forms.Form):
    name = forms.CharField(label=u'姓名',required = False, max_length=200)
    account = forms.CharField(label=u'登陆账号',required =True,  max_length=200)
    password = forms.CharField(label=u'密码',required = True,  max_length=1024)
    mobile = forms.CharField(label=u'电话',required = False,  max_length=200)
    email = forms.CharField(label=u'邮箱',required = False, max_length=200)
    flag = forms.IntegerField(label=u'级别',required = False, )
    linkid = forms.CharField(label=u'关联ID',required = False,  max_length=200)

# list of mobile User Agents
mobile_uas = [
	'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
	'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
	'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
	'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
	'newt','noki','oper','palm','pana','pant','phil','play','port','prox',
	'qwap','sage','sams','sany','sch-','sec-','send','seri','sgh-','shar',
	'sie-','siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-',
	'tosh','tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp',
	'wapr','webc','winw','winw','xda','xda-'
	]
 
mobile_ua_hints = [ 'SymbianOS', 'Opera Mini', 'iPhone' ]
 
 
def mobileBrowser(request):
    ''' Super simple device detection, returns True for mobile devices '''
 
    mobile_browser = False
    ua = request.META['HTTP_USER_AGENT'].lower()[0:4]
 
    if (ua in mobile_uas):
        mobile_browser = True
    else:
        for hint in mobile_ua_hints:
            if request.META['HTTP_USER_AGENT'].find(hint) > 0:
                mobile_browser = True
 
    return mobile_browser

def booklist(request):
    data = None
    if request.method == 'POST':
        form = ListSearchForm(request.POST, request.FILES)
        print request.POST
        if form.is_valid():
                try:
                    keyword = form.cleaned_data['search'].strip()
                    data = session.query(BookSL).filter(
                        and_(
                          BookSL.id > 0 if keyword == "" else  
                          or_(
                            BookSL.name.like('%%%s%%'%(keyword)),
                            BookSL.author.like('%%%s%%'%(keyword)),
                            ),
                          )
                    ).order_by(desc(BookSL.id)).all()
                    print data
                except Exception,e:
                    error = u"文件保存失败.请联系管理员"
                    session.rollback()
                    printError()
        else:
            print "not valid"                
    else:
        data = session.query(BookSL).order_by(desc(BookSL.id)).all()[:10]
        form = ListSearchForm()
    return render(request, 'manage/bookList.html', {'form': form, 'data' : data })    


#### use uploadify for professional   
def upload(request):
    info = ''
    error = ''

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        print request.POST
        if form.is_valid():
            print "not valid"                
            f = request.FILES['file']
            filename = handle_uploaded_file(f, form.cleaned_data['bookclass'].strip())
            if filename == "":
                error = u"文件保存失败.请联系管理员"
            else:
                data = BookSL()
                try:
                    
                    session.add(data)
                    update_model(data, form.cleaned_data)
                    data.name, data.format = os.path.splitext(os.path.basename(f.name))
                    data.format = data.format[1:].lower()
                    data.uploadtime = datetime.datetime.now()
                    data.path = os.path.relpath( filename, settings.BOOK_BASE)
                    data.uploader = ''
                    data.bookid =  '%s' % (uuid.uuid1())
                    data.cost = 0
                    data.counter = 0
                    
                    session.commit()
                    info = '上传成功!'
                    
                    r = syncBatchBooks.delay(filename)
                    print "sync book job:", r
                    return HttpResponseRedirect('/docview/manage/book/')
                except Exception,e:
                    error = u"文件保存失败.请联系管理员"
                    session.rollback()
                    printError()
        else:
            field, einfo = form.errors.items()[0]
            error = form[field].label +":" +  einfo.as_text()              
    else:
        print "form get"
        form = UploadFileForm()
    return render(request, 'manage/bookUpload.html', {'form': form, 'info':info, 'error':error })
    
def bookedit(request, bookid):
    info = ''
    error = ''
    print bookid
    data = session.query(BookSL).filter(
                        and_(BookSL.id == bookid,
                        )).first()
    if request.method == 'POST':
        form = UploadFileForm(request.POST)
        form.fields.pop('file', None)
        if form.is_valid():
            try:
                update_model(data, form.cleaned_data)
                session.commit()
                info = '保存成功!'
                return HttpResponseRedirect('/docview/manage/book/')
            except Exception,e:
                error = u"信息修改失败.请联系管理员"
                session.rollback()
                printError()
        else:
            field, einfo = form.errors.items()[0]
            error = form[field].label +":" +  einfo.as_text()              
    else:
        form = UploadFileForm(initial=data.__dict__)
        form.fields.pop('file', None)
        
    return render(request, 'manage/bookEdit.html', {'form': form, 'info':info, 'error':error })    
    
def bookdelete(request, bookid):
    info = ''
    error = ''
    print bookid
    try:
        data = session.query(BookSL).filter(
                            and_(BookSL.id == bookid,
                            )).first()
        
        if data.path != None and data.path.strip() != '':
            path = data.path.strip()
            if path[0] != '/' and path[0] != '\\':
                path = os.path.join( settings.BOOK_BASE, data.path )
                if os.path.isfile(path):
                    try:
                        os.remove(path)
                    except Exception,e:
                        printError()            
        session.delete(data)
        session.commit()
        
    except Exception,e:
        error = u"文档删除失败.请联系管理员"
        session.rollback()
        printError()            
    return HttpResponseRedirect('/docview/manage/book/')        
    
    
def handle_uploaded_file(f, todir):
    filename = os.path.join(  os.path.join( settings.BOOK_BASE,todir), f.name)
    try:
        logging.info("saving file:%s", filename )
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)    
        return filename                
    except Exception, e:
        return ""
        printError()     
        
#### use uploadify for professional   
def search(request):
    return render(request, 'search.html', { })                   
    
def userlist(request):
    data = None
    if request.method == 'POST':
        form = ListSearchForm(request.POST, request.FILES)
        print request.POST
        if form.is_valid():
                try:
                    keyword = form.cleaned_data['search'].strip()
                    data = session.query(UserSL).filter(
                        and_(
                          UserSL.id > 0 if keyword == "" else  
                          or_(
                            UserSL.name.like('%%%s%%'%(keyword)),
                            UserSL.account.like('%%%s%%'%(keyword)),
                            UserSL.mobile.like('%%%s%%'%(keyword)),
                            UserSL.email.like('%%%s%%'%(keyword)),
                            UserSL.linkid.like('%%%s%%'%(keyword)),
                            ),
                          )
                    ).order_by(desc(UserSL.id)).all()
                    print data
                except Exception,e:
                    error = u"获取用户列表失败.请联系管理员"
                    session.rollback()
                    printError()
        else:
            print "not valid"                
    else:
        data = session.query(UserSL).order_by(desc(UserSL.id)).all()[:10]
        form = ListSearchForm()
    return render(request, 'manage/userList.html', {'form': form, 'data' : data })       
        
def useredit(request, userid):
    info = ''
    error = ''
    print userid
    data = session.query(UserSL).filter(
                        and_(UserSL.id == userid,
                        )).first()
    if request.method == 'POST':
        form = UserInfoForm(request.POST)
        if form.is_valid():
            try:
                a = session.query(UserSL).filter(
                        and_(
                            UserSL.account == form.cleaned_data['account'],
                            UserSL.id != userid,
                            ),
                    ).all()                
                if len(a) > 0:
                    error = u"登陆名已存在!"
                else:                    
                    update_model(data, form.cleaned_data)
                    session.commit()
                    info = '保存成功!'
                    return HttpResponseRedirect('/docview/manage/user/')
            except Exception,e:
                error = u"信息修改失败.请联系管理员"
                session.rollback()
                printError()
        else:
            field, einfo = form.errors.items()[0]
            error = form[field].label +":" +  einfo.as_text()              
    else:
        form = UserInfoForm(initial=data.__dict__)
        
    return render(request, 'manage/userEdit.html', {'form':form, 'info':info, 'error':error })            
        
def userdelete(request, userid):
    info = ''
    error = ''
    print userid
    try:
        data = session.query(UserSL).filter(
                            and_(UserSL.id == userid,
                            )).first()
        session.delete(data)
        session.commit()
    except Exception,e:
        error = u"用户删除失败.请联系管理员"
        session.rollback()
        printError()            
    return HttpResponseRedirect('/docview/manage/user/')        
     