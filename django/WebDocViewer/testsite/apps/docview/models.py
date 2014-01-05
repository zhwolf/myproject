# -*- coding: utf-8 -*-

from django.db import models

# Create your models here.

from django import forms

class UploadFileForm(forms.Form):
  keywords = forms.CharField(label=u'关键字', max_length=200)
  file = forms.FileField(label=u'上传')