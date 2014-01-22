from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from haystack.views import SearchView, search_view_factory
import views,views_manage, views_users

urlpatterns = patterns('',
    #url(r'^$', views.index, name='index' ),
    
    url(r'^showswf/+(?P<path>.*)/$', views.getswf, name='getdoc' ),
    url(r'^showpdf/+(?P<path>.*)/$', views.getpdf, name='getdoc' ),
    url(r'^view/+(?P<path>.*)/$', views.view, name='view' ),
    url(r'^pdfviewer/', TemplateView.as_view(template_name="pdfviewer.html") ),

    url(r'^search/$', search_view_factory(view_class=views.BookSearchView, load_all=False, template='search/search.html', form_class=views.BookSearchForm), name='book_search'),
    
    
    url(r'^manage/book/$', views_manage.booklist, name='doc_manage_index' ),
    url(r'^manage/bookupload/$', views_manage.upload, name='doc_manage_upload' ),
    url(r'^manage/bookedit/+(?P<bookid>.*)/$', views_manage.bookedit, name='doc_manage_bookedit' ),
    url(r'^manage/bookdelete/+(?P<bookid>.*)/$', views_manage.bookdelete, name='doc_manage_bookdelete' ),

    url(r'^manage/user/$', views_manage.userlist, name='user_manage_index' ),
    url(r'^manage/useredit/+(?P<userid>.*)/$', views_manage.useredit, name='manage_useredit' ),
    url(r'^manage/userdelete/+(?P<userid>.*)/$', views_manage.userdelete, name='manage_userdelete' ),


    url(r'^user/register/+(?P<regtype>.*?)/*$', views_users.register, name='user_register' ),


    url(r'^login/+@*(?P<path>.*)$', views.login, name='login' ),
    url(r'^logout/$', views.logout, name='logout' ),
)
