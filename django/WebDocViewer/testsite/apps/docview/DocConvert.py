from __future__ import absolute_import
# -*- coding: utf-8 -*-

import subprocess 
import os
import logging
import sys
import traceback
import StringIO
import locale
import threading
import Queue
import uuid
DEFAULT_ENCODE =  sys.stdin.encoding if sys.stdin.encoding else locale.getdefaultlocale()[1] if locale.getdefaultlocale()[1]  else sys.getdefaultencoding()


#pdf_lock = threading.Lock() 

OfficePortQueue = Queue.Queue()
#for i in range(10):
#    OfficePortQueue.put(2002 + i)
OfficePortQueue.put(2002)

class DocConverter:
    def __init__(self,basedir,outputdir,toolbasedir, errfunc):
        self.basedir = basedir
        self.outputdir = outputdir
        self.toolbasedir = toolbasedir
        self.printError = errfunc
        SWFTOOL_BASE= os.path.join(self.toolbasedir, "tools/SWFTools")
        self.SWFTOOLS = {
            'font': os.path.join(SWFTOOL_BASE, "font2swf.exe"),
            'gif' : os.path.join(SWFTOOL_BASE, "gif2swf.exe"),
            'gpdf': os.path.join(SWFTOOL_BASE, "gpdf2swf.exe"),
            'jpeg': os.path.join(SWFTOOL_BASE, "jpeg2swf.exe"),
            'jpg': os.path.join(SWFTOOL_BASE, "jpeg2swf.exe"),
            'pdf': os.path.join(SWFTOOL_BASE, "pdf2swf.exe"),
            'png': os.path.join(SWFTOOL_BASE, "png2swf.exe"),
            'wav': os.path.join(SWFTOOL_BASE, "wav2swf.exe"),
        }        
        self.UNOCONVTOOL= os.path.join(self.toolbasedir, "tools/unoconv/unoconv")
        self.PDF2TXT = os.path.join(self.toolbasedir, "tools/unoconv/pdf2txt.py")

    def getswf(self, fullpath,basedir=None, outputdir=None):
        if None or not fullpath:
            return ''        
        if basedir == None:
            basedir=self.basedir
        if outputdir == None:
            outputdir=self.outputdir
        try:
            fullpath = fullpath.strip()
            relate_path = os.path.relpath( fullpath, basedir)
            sufix = os.path.splitext(fullpath)[1][1:].lower()
            logging.info( "getswf:%s, relate_path:%s, basedir:%s",sufix, relate_path, basedir)
            if sufix != 'swf' :
                cmdpath = self.SWFTOOLS.get(sufix, None)
                apath = ""
                if cmdpath == None:
                    fullpath = self.convert2pdf(fullpath, os.path.join( outputdir , relate_path ))   
                fullpath = self.convert2swf(fullpath, os.path.join( outputdir , relate_path ))
            return fullpath
        except Exception, e:
            self.printError()       

    def getswfFromRelpath(self, relpath):
        return self.getswf( os.path.join(self.basedir, path).strip())

    def gettxt(self, fullpath,basedir=None, outputdir=None):
        if None or not fullpath:
            return ''
        if basedir == None:
            basedir=self.basedir
        if outputdir == None:
            outputdir=self.outputdir
        
        try:
            fullpath = fullpath.strip()
            relate_path = os.path.relpath(fullpath, basedir)
            sufix = os.path.splitext(fullpath)[1][1:].lower()
            logging.info( "getpdf:%s",sufix    )
            if sufix != 'pdf' :
                fullpath = self.convert2pdf(fullpath, os.path.join( outputdir , relate_path ))   
            fullpath =   self.convert2txt(fullpath, os.path.join( outputdir , relate_path ))
            return fullpath
        except Exception, e:
            self.printError()    
                
    def getpdf(self, fullpath,basedir=None, outputdir=None):
        if None or not fullpath:
            return ''        
        if basedir == None:
            basedir=self.basedir
        if outputdir == None:
            outputdir=self.outputdir
        
        try:
            fullpath = fullpath.strip()
            relate_path = os.path.relpath(fullpath, basedir)
            sufix = os.path.splitext(fullpath)[1][1:].lower()
            logging.info( "getpdf:%s",sufix    )
            if sufix != 'pdf' :
                fullpath = self.convert2pdf(fullpath, os.path.join( outputdir , relate_path ))   
            else:
                convert2txt(fullpath, os.path.join( outputdir , relate_path ))
            return fullpath
        except Exception, e:
            self.printError()                

    def getpdfFromRelpath(self, relpath):
        return self.getpdf( os.path.join(self.basedir, path).strip())
            
        
    def convert2swf(self,fullpath, todir):
        logging.info("convert %s to swf", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
        swffile = os.path.join(todir, 'swf/transfered.swf')
        
        if os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", fullpath)
            return swffile
        
        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()            
        
        cmdpath = self.SWFTOOLS.get(sufix, None)
        logging.info('path:%s sufix:%s cmdpath:%s', path, sufix, cmdpath)
        if cmdpath == None:
            return ""
        #ret, logs = self.execmd( r'"%s" "%s" -o "%s"  -T 9 -G' % (cmdpath, fullpath, swffile) )
        ret, logs = self.execmd( r'"%s" "%s" -o "%s"  -T 9 -G -s poly2bitmap' % (cmdpath, fullpath, swffile) )
        if ret:
            return swffile
        elif ret==1:
            return ""
    
    def convert2pdf(self,fullpath,todir):
        logging.info("convert %s to pdf", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
            
        thisfile = '%s.pdf' %(os.path.splitext(fullpath)[0])
        swffile = os.path.join(todir, 'pdf/transfered.pdf' )

        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()            
        
        if os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", fullpath)
        else:
            cmdpath = self.UNOCONVTOOL
            port = OfficePortQueue.get()
            try:
                #pdf_lock.acquire()
                ret, logs = self.execmd( r'python "%s" -f pdf -p %s "%s"' % (cmdpath,port, fullpath) )
                OfficePortQueue.put(port)
            except Exception,e:
                OfficePortQueue.put(port+1)
                self.printError()
                return ""
            finally:
                #pdf_lock.release()            
                pass
                            
            if ret:
                logging.info( "thisfile:%s    swffile:%s",thisfile,  swffile)
                try:
                    os.remove(swffile)
                except Exception,e:
                    pass
                os.rename(thisfile, swffile)
            elif ret==1:
                return ""
            
        #now convert to text
        self.convert2txt( swffile, todir)
                      
        return swffile
     
    def convert2txt(self,fullpath,todir):
        logging.info("convert %s to txt", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
        swffile = os.path.join(todir, 'txt/transfered.txt')
        
        if os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", fullpath)
            return swffile
        
        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()            


        cmdpath = self.PDF2TXT
        try:
            #pdf2txt.py -o output.html samples/naacl06-shinyama.pdf
            ret, logs = self.execmd( r'python "%s" -o "%s" "%s"' % (cmdpath,swffile, fullpath) )
        except Exception,e:
            self.printError()
            return ""
        finally:
            pass        
                
        if ret:
            return swffile
        elif ret==1:
            return ""        
        
    def execmd(self,cmd):
        #cmd = cmd.encode(DEFAULT_ENCODE)
        cmd = cmd.encode(DEFAULT_ENCODE) 
        try:
            process =subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            output= process.communicate()        #这里就是我们所需要的stdout的编码格式
            ret = process.wait()
            #output= process.communicate()        #这里就是我们所需要的stdout的编码格式
            logging.info("cmd: %s result:%s output:%s", cmd, ret, output )
            if ret==0:
                print 'DONE!'
                return True, output
            elif ret==1:
                print 'FAILED!'
                return False, output    
        except Exception,e:
            self.printError()                
            pass
        finally:
            process.kill()                