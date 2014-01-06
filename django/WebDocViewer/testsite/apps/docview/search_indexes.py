# -*- coding: utf-8 -*-
from haystack import indexes, site
from apps.products.models import Product
 
 
class ProductIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='name')
 
 
    def get_model(self):
        return Product
 
    def index_queryset(self):
        return self.get_model().objects.all()
 
site.register(Product, ProductIndex)