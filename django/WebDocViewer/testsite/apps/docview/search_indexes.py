# -*- coding: utf-8 -*-
from haystack import indexes
from .models import Book
 
 
class BookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name    = indexes.CharField(model_attr='name', boost= 5.0)
    author  = indexes.CharField(model_attr='author',  boost=3.0)
    descr    = indexes.CharField(model_attr='descr')
    tags    = indexes.CharField(model_attr='tags')
    summary = indexes.CharField(model_attr='summary')
        
    def get_model(self):
        return Book
 
    def index_queryset(self):
        return self.get_model().objects.all()