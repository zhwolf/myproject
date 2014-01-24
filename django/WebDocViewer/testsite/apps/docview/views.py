# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
from django.utils.encoding import force_text
from apps.backends.DBEnginee.djSQLAlchemy import Session,update_model
from sqlalchemy.sql import and_,or_, desc
from .models import Book, BookSL, UserSL
from .tasks import syncBatchBooks
from shared.utils import printError, DEFAULT_ENCODE

from .DocConvert import DocConverter
import datetime
import uuid

import subprocess 

import jieba
    


from haystack.forms import SearchForm, ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Exact, Clean
from haystack.views import SearchView, search_view_factory


session = Session()

class BookSearchView(SearchView):
    def extra_context(self):
        extra = super(BookSearchView, self).extra_context()
        #extra['top_tags'] = Tag.objects.all().annotate(num_items=Count('doubanmovie')).order_by('-num_items')[0:33]
        return extra
        
    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        """
        (paginator, page) = self.build_page()

        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'suggestion': None,
            'keywords' : " ".join(jieba.cut_for_search(self.query))
        }

        if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()

        context.update(self.extra_context())
        return render_to_response(self.template, context, context_instance=self.context_class(self.request))        

class BookSearchForm(SearchForm):
    def get_result_id(self, id):
        return id
        
    def __init__(self, *args, **kwargs):
        super(BookSearchForm, self).__init__(*args, **kwargs)
        
    def search(self):
        print 'test............'
        if not self.is_valid():
            print 'is not valid............'
            return self.no_query_found()
        if not  self.cleaned_data.get('q'):
            print 'no cleaned data............'
            #return self.no_query_found()
        '''
        print 'search in form:', self.cleaned_data['q']
        #return super(BookSearchForm, self).search()
        return self.searchqueryset.filter_or(content=self.cleaned_data['q'])
        '''
        
        query = self.cleaned_data['q']

        words=jieba.cut_for_search(query)  
        
        sqs = self.searchqueryset.filter(content=query) # actually I have one more field here...
        for word in words:
            sqs = sqs.filter_or(content=word)
        return sqs
        
class LoginForm(forms.Form):
    account = forms.CharField(label=u'账号',required = True, max_length=200,error_messages = {
           'required': u'账号不能为空',}
            )
    password = forms.CharField(label=u'密码',required = True, max_length=200,error_messages = {
           'required': u'密码不能为空',}
            )

class Any:
    pass

    
def login(request, path):
    error = ''
    refer = path.strip()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
                try:
                    data = session.query(UserSL).filter(
                        and_(
                            UserSL.account == form.cleaned_data['account'],
                            UserSL.password == form.cleaned_data['password'],
                          )
                    ).all()[:2]
                    if len(data) > 1:
                        error = u'内部错误,请联系管理员'
                    elif len(data) != 1:
                        error = u'错误的账号或密码'
                    else:    
                        data = data[0]
                        request.session['user'] = data.account
                        request.session['userid'] = data.id
                        request.session['userkey'] = data.userid
                        request.session['admin'] = 1 if data.flag ==1 else 0
                        
                        if refer == '':
                            return HttpResponseRedirect('/')
                        else:    
                            return HttpResponseRedirect('refer')
                except Exception,e:
                    error = u"登陆时发生内部错误.请联系管理员"
                    session.rollback()
                    printError()
        else:
            field, info = form.errors.items()[0]
            error = info.as_text()
            
    else:
        form = LoginForm()
    #return render(request, 'login.html', {'error' : error, 'refer':refer, 'menudata': "" })    
    return render_to_response('login.html', {'error' : error, 'refer':refer }, context_instance=RequestContext(request) )    
        
def logout(request):
    request.session.clear()        
    return HttpResponseRedirect('/')

def view(request, path):
    fullapth = os.path.join(settings.BOOK_BASE, path)
    f = os.path.basename(path)
    sufix = os.path.splitext(path)[1][1:].lower()
    any = Any()
    any.name = f
    any.abpath = r"/" + f
    any.fullpath= path
    any.size = os.path.getsize(fullapth)
    any.time = os.path.getctime(fullapth)
    print request.META['HTTP_USER_AGENT']
    
    if  request.META['HTTP_USER_AGENT'].find('MSIE') >=0 or sufix == 'swf':
        html = 's_viewswf.html'
        #return render(request, 's_viewswf.html', { 'file' : any, } )
    else:       
        html = 's_viewpdf.html' 
        #return render(request, 's_viewpdf.html', { 'file' : any, } )
    return render_to_response(html, { 'file' : any, } , context_instance=RequestContext(request) )    
    
def getswf(request,path):
    converter = DocConverter(settings.BOOK_BASE, settings.BOOK_OUTPUT_BASE,settings.BASE_DIR, printError)
    fullpath = os.path.join(settings.BOOK_BASE, path).strip()
    fullpath = converter.getswf(fullpath)    
    return bigFileView(request, fullpath )

def getpdf(request,path):
    converter = DocConverter(settings.BOOK_BASE, settings.BOOK_OUTPUT_BASE,settings.BASE_DIR, printError)
    fullpath = os.path.join(settings.BOOK_BASE, path).strip()
    fullpath = converter.getpdf(fullpath)    
    return bigFileView(request, fullpath )

def bigFileView(request, file_name):
    # do something...
    def readFile(fn, buf_size=262144):
        f = open(fn, "rb")
        while True:
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()
    response = HttpResponse(readFile(file_name))
    return response
  
        
#### use uploadify for professional   
def search(request):
    #return render(request, 'search.html', { })                   
    render_to_response('search.html', {} , context_instance=RequestContext(request) )    
    
def classview(request, path):
    data = None
    import chardet
    print path, chardet.detect(path)
    try:
        data = session.query(BookSL).filter(
            and_(
                BookSL.bookclass.like('%%%s%%'%(path)), 
              )).order_by(desc(BookSL.counter)).all()[:20]
        print data              
    except Exception,e:
        error = u"登陆时发生内部错误.请联系管理员"
        session.rollback()
        printError()
    return render_to_response('classview.html', {'data' : data }, context_instance=RequestContext(request) )            
                              