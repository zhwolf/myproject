from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from haystack.views import SearchView, search_view_factory
import views

urlpatterns = patterns('',
    url(r'^$', views.upload, name='index' ),
    url(r'^showswf/+(?P<path>.*)', views.getswf, name='getdoc' ),
    url(r'^showpdf/+(?P<path>.*)', views.getpdf, name='getdoc' ),
    url(r'^upload/$', views.upload, name='upload' ),
    url(r'^view/+(?P<path>.*)', views.view, name='view' ),
    
    url(r'test/$', TemplateView.as_view(template_name="test.html") ),
    url(r'viewer/$', TemplateView.as_view(template_name="viewer.html") ),
    
    #url(r'^search/$', views.search, name='search' ),
    
    #url(r'^search/', include('haystack.urls')),
    url(r'^search/$', search_view_factory(view_class=views.BookSearchView, load_all=False, template='search/search.html', form_class=views.BookSearchForm), name='book_search'),
)
