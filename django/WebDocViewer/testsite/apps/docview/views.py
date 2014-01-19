# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms

from .DocConvert import DocConverter

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

class UploadFileForm(forms.Form):
  keywords = forms.CharField(label=u'关键字', max_length=200)
  file = forms.FileField(label=u'上传')

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
def upload(request):
    info = ''

    abpath = settings.BOOK_ABSPATH
    path = settings.BOOK_BASE
    files = []
    fs = os.listdir(path)
    for of in fs:
        f = unicode(of, DEFAULT_ENCODE)
        fullpath = os.path.join(path, f) 
        if os.path.isfile(fullpath) :
            print f
            any = Any()
            any.name = f
            any.abdir = r"/" + abpath
            any.abpath = r"/" + f
            any.fullpath= fullpath
            sufix = os.path.splitext(f)[1][1:]
            files.append( any)


    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            info = '上传成功!'
            return HttpResponseRedirect('/docview/upload/')
    else:
        form = UploadFileForm()
            
    return render(request, 'upload.html', {'form': form, 'files' : files, 'info':info })
    
def handle_uploaded_file(f):
    filename = os.path.join(settings.BOOK_BASE, f.name)
    try:
        logging.info("saving file:%s", filename )
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)    
    except Exception, e:
        printError()     
        
#### use uploadify for professional   
def search(request):
    return render(request, 'search.html', { })                   