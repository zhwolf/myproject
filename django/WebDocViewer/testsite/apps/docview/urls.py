from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from haystack.views import SearchView, search_view_factory
import views
import views_manage

urlpatterns = patterns('',
    #url(r'^$', views.index, name='index' ),
    
    url(r'^showswf/+(?P<path>.*)/$', views.getswf, name='getdoc' ),
    url(r'^showpdf/+(?P<path>.*)/$', views.getpdf, name='getdoc' ),
    url(r'^view/+(?P<path>.*)/$', views.view, name='view' ),
    url(r'^pdfviewer/', TemplateView.as_view(template_name="pdfviewer.html") ),

    url(r'^search/$', search_view_factory(view_class=views.BookSearchView, load_all=False, template='search/search.html', form_class=views.BookSearchForm), name='book_search'),
    
    
    url(r'^manage/$', views_manage.booklist, name='manage_index' ),
    url(r'^manage/upload/$', views_manage.upload, name='manage_upload' ),
    url(r'^manage/bookedit/+(?P<bookid>.*)/$', views_manage.bookedit, name='manage_bookedit' ),
    url(r'^manage/bookdelete/+(?P<bookid>.*)/$', views_manage.bookdelete, name='manage_bookdelete' ),
    
)
