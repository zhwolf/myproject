# -*- coding: utf-8 -*-
from haystack import indexes, site
from .models import Book
 
 
class BookIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
 
    def get_model(self):
        return Book
 
    def index_queryset(self):
        return self.get_model().objects.all()
 
site.register(Book, BookIndex)