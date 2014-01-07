# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.

from django import forms


class Book(models.Model):
    name    =models.CharField(u'名称',max_length=250,blank=False)
    author  =models.CharField(u'作者',max_length=200,blank=True)
    desc    =models.CharField(u'简介',max_length=500,blank=True)
    tags    =models.CharField(u'标签',max_length=200,blank=True)
    summary =models.CharField(u'摘要',max_length=2048,blank=True)
    path    =models.CharField(u'路径',max_length=500,blank=True)
    format  =models.CharField(u'格式',max_length=10,blank=True)
    uploadtime  =models.CharField(u'上传时间',max_length=20,blank=True)
    uploader    =models.CharField(u'上传人',max_length=50,blank=True)
   
    def __unicode__(self):
        return self.name
    class Meta:
        db_table = 'book'

class UploadFileForm(forms.Form):
  keywords = forms.CharField(label=u'关键字', max_length=200)
  file = forms.FileField(label=u'上传')
  
  