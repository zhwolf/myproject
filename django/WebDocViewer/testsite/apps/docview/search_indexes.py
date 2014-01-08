# -*- coding: utf-8 -*-
from haystack import indexes
from .models import Book
 
 
class BookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name    = indexes.CharField( boost= 5.0)
    author  = indexes.CharField(null=True,  boost=3.0)
    descr    = indexes.CharField(null=True,)
    tags    = indexes.CharField(null=True,)
    summary = indexes.CharField(null=True,)
        
    def get_model(self):
        return Book
 
    def index_queryset(self,  using=None):
        return self.get_model().objects.all()
        
    def prepare_name(self,obj):
        return obj.name if obj.name else ""
        
    def prepare_author(self,obj):
        return obj.author if obj.author else ""      

    def prepare_descr(self,obj):
        return obj.descr if obj.descr else ""             

    def prepare_tags(self,obj):
        return obj.tags if obj.tags else ""   
        
    def prepare_summary(self,obj):
        return obj.summary if obj.summary else ""           