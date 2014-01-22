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
from .models import Book, BookSL
from .tasks import syncBatchBooks

from .DocConvert import DocConverter
import datetime
import uuid

import subprocess 
import os
import logging
import sys
import traceback
import StringIO
import jieba
    


from haystack.forms import SearchForm, ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Exact, Clean
from haystack.views import SearchView, search_view_factory

DEFAULT_ENCODE =  sys.stdin.encoding if sys.stdin.encoding else locale.getdefaultlocale()[1] if locale.getdefaultlocale()[1]  else sys.getdefaultencoding()

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

class Any:
    pass

def printError():
    fp = StringIO.StringIO()
    traceback.print_exc(file=fp)
    ret = fp.getvalue()
    logging.error("exception:%s",ret)

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
        return render(request, 's_viewswf.html', { 'file' : any, } )
    else:        
        return render(request, 's_viewpdf.html', { 'file' : any, } )
    
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
    return render(request, 'search.html', { })                   