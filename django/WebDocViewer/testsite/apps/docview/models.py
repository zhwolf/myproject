# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
import sys

from sqlalchemy import Table, Column, Integer, String, ForeignKey, MetaData
from sqlalchemy.orm import mapper
from apps.backends.DBEnginee.djSQLAlchemy import metadata
# Create your models here.

class Book(models.Model):
    bookid  =models.CharField(u'bookid',max_length=250,blank=False)
    name    =models.CharField(u'名称',max_length=250,blank=False)
    author  =models.CharField(u'作者',max_length=200,blank=True)
    descr    =models.CharField(u'简介',max_length=500,blank=True)
    tags    =models.CharField(u'标签',max_length=200,blank=True)
    summary =models.CharField(u'摘要',max_length=2048,blank=True)
    path    =models.CharField(u'路径',max_length=500,blank=True)
    format  =models.CharField(u'格式',max_length=10,blank=True)
    uploadtime  =models.CharField(u'上传时间',max_length=20,blank=True)
    uploader    =models.CharField(u'上传人',max_length=50,blank=True)
    flag        =models.IntegerField(u'上传人',max_length=50,blank=True)
    cost        =models.IntegerField(u'上传人',max_length=50,blank=True)
    counter    =models.IntegerField(u'上传人',max_length=50,blank=True)
    def __unicode__(self):
        return self.name.encode(sys.stdin.encoding)
        
    class Meta:
        db_table = 'b_book'

#sqlalchemy book
Book_table=Table("b_book", metadata, autoload=True)
class BookSL(object):
    pass
mapper(BookSL, Book_table)  

#sqlalchemy book
User_table=Table("b_user", metadata, autoload=True)
class UserSL(object):
    pass
mapper(UserSL, User_table)  
  

UserBook_table=Table("b_user_book", metadata, autoload=True)
class UserBookSL(object):
    pass
mapper(UserBookSL, UserBook_table)  
  
  