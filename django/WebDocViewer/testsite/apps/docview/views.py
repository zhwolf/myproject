# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from .models import UploadFileForm

import subprocess 
import os
import logging
import sys
import traceback
import StringIO

class Any:
    pass
    
DEFAULT_ENCODE = sys.stdin.encoding

# list of mobile User Agents
mobile_uas = [
	'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
	'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
	'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
	'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
	'newt','noki','oper','palm','pana','pant','phil','play','port','prox',
	'qwap','sage','sams','sany','sch-','sec-','send','seri','sgh-','shar',
	'sie-','siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-',
	'tosh','tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp',
	'wapr','webc','winw','winw','xda','xda-'
	]
 
mobile_ua_hints = [ 'SymbianOS', 'Opera Mini', 'iPhone' ]
 
 
def mobileBrowser(request):
    ''' Super simple device detection, returns True for mobile devices '''
 
    mobile_browser = False
    ua = request.META['HTTP_USER_AGENT'].lower()[0:4]
 
    if (ua in mobile_uas):
        mobile_browser = True
    else:
        for hint in mobile_ua_hints:
            if request.META['HTTP_USER_AGENT'].find(hint) > 0:
                mobile_browser = True
 
    return mobile_browser

def printError():
    fp = StringIO.StringIO()
    traceback.print_exc(file=fp)
    ret = fp.getvalue()
    logging.error("exception:%s",ret)

def view(request, path):
    fullapth = os.path.join(settings.BOOK_BASE, path)
    f = os.path.basename(path)
    sufix = os.path.splitext(path)[1][1:].lower()
    any = Any()
    any.name = f
    any.abpath = r"/" + f
    any.fullpath= path
    any.size = os.path.getsize(fullapth)
    any.time = os.path.getctime(fullapth)
    
    if  request.META['HTTP_USER_AGENT'].find('MSIE') >=0 or sufix == 'swf':
        return render(request, 'viewswf.html', { 'file' : any, } )
    else:        
        return render(request, 'viewpdf.html', { 'file' : any, } )
    
def getswf(request,path):
    try:
        relate_path = os.path.dirname(path)
        fullpath = os.path.join(settings.BOOK_BASE, path).strip()
        sufix = os.path.splitext(fullpath)[1][1:].lower()
        if sufix != 'swf' :
            cmdpath = settings.SWFTOOLS.get(sufix, None)
            apath = ""
            if cmdpath == None:
                fullpath = convert2pdf(fullpath, os.path.join(settings.BOOK_OUTPUT_BASE , relate_path ))   
            fullpath = convert2swf(fullpath, os.path.join(settings.BOOK_OUTPUT_BASE , relate_path ))
        return bigFileView(request, fullpath )
    except Exception, e:
        printError()       

def getpdf(request,path):
    try:
        relate_path = os.path.dirname(path)
        fullpath = os.path.join(settings.BOOK_BASE, path).strip()
        sufix = os.path.splitext(fullpath)[1][1:].lower()
        if sufix != 'pdf' :
            fullpath = convert2pdf(fullpath, os.path.join(settings.BOOK_OUTPUT_BASE , relate_path ))   
        return bigFileView(request, fullpath )
    except Exception, e:
        printError()               

def convert2swf(fullpath, todir):
    logging.info("convert %s to swf", fullpath)
    path = os.path.basename( fullpath)
    fs = os.path.splitext(path)
    filename = fs[0]
    sufix = fs[1][1:].lower().strip()
    swffile = os.path.join(todir, '%s.swf' %(filename))
    
    if os.path.isfile(swffile):
        logging.info("Good. File already exists:%s", fullpath)
        return swffile
    
    
    cmdpath = settings.SWFTOOLS.get(sufix, None)
    print path, sufix, cmdpath
    if cmdpath == None:
        return ""
    ret, logs = execmd( r'"%s" "%s" -o "%s"  -T 9 -G -s poly2bitmap' % (cmdpath, fullpath, swffile) )
    if ret:
        return swffile
    elif ret==1:
        return ""

def convert2pdf(fullpath,todir):
    logging.info("convert %s to pdf", fullpath)
    path = os.path.basename( fullpath)
    fs = os.path.splitext(path)
    filename = fs[0]
    sufix = fs[1][1:].lower().strip()
    thisfile = '%s.pdf' %(os.path.splitext(fullpath)[0])
    swffile = os.path.join(todir, '%s.pdf' %(filename))
    
    if os.path.isfile(swffile):
        logging.info("Good. File already exists:%s", fullpath)
        return swffile
    
    cmdpath = settings.UNOCONVTOOL
    ret, logs = execmd( r'python "%s" -f pdf "%s"' % (cmdpath, fullpath) )
    if ret:
        try:
            os.remove(swffile)
        except Exception,e:
            pass
        os.rename(thisfile, swffile)
        return swffile
    elif ret==1:
        return ""
 

def execmd(cmd):
    cmd = cmd.encode(DEFAULT_ENCODE)
    process =subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    ret = process.wait()
    output= process.communicate()        #这里就是我们所需要的stdout的编码格式
    logging.info("cmd: %s result:%s output:%s", cmd, ret, output )
    if ret==0:
        print 'DONE!'
        return True, output
    elif ret==1:
        print 'FAILED!'
        return False, output
    


def bigFileView(request, file_name):
    # do something...
    def readFile(fn, buf_size=262144):
        f = open(fn, "rb")
        while True:
            c = f.read(buf_size)
            if c:
                yield c
            else:
                break
        f.close()
    response = HttpResponse(readFile(file_name))
    return response

#### use uploadify for professional   
def upload(request):
    info = ''

    abpath = settings.BOOK_ABSPATH
    path = settings.BOOK_BASE
    files = []
    fs = os.listdir(path)
    for of in fs:
        f = unicode(of, DEFAULT_ENCODE)
        fullpath = os.path.join(path, f) 
        if os.path.isfile(fullpath) :
            print f
            any = Any()
            any.name = f
            any.abdir = r"/" + abpath
            any.abpath = r"/" + f
            any.fullpath= fullpath
            sufix = os.path.splitext(f)[1][1:]
            files.append( any)


    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            info = '上传成功!'
            return HttpResponseRedirect('/docview/upload/')
    else:
        form = UploadFileForm()
            
    return render(request, 'upload.html', {'form': form, 'files' : files, 'info':info })
    
def handle_uploaded_file(f):
    filename = os.path.join(settings.BOOK_BASE, f.name)
    try:
        logging.info("saving file:%s", filename )
        with open(filename, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)    
    except Exception, e:
        printError()                