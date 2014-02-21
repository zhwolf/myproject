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
import shutil
from pdfminer.pdfpage import PDFPage
DEFAULT_ENCODE =  sys.stdin.encoding if sys.stdin.encoding else locale.getdefaultlocale()[1] if locale.getdefaultlocale()[1]  else sys.getdefaultencoding()


pdf_lock = threading.Lock() 

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
            #'gif' : os.path.join(SWFTOOL_BASE, "gif2swf.exe"),
            'gpdf': os.path.join(SWFTOOL_BASE, "gpdf2swf.exe"),
            #'jpeg': os.path.join(SWFTOOL_BASE, "jpeg2swf.exe"),
            #'jpg': os.path.join(SWFTOOL_BASE, "jpeg2swf.exe"),
            'pdf': os.path.join(SWFTOOL_BASE, "pdf2swf.exe"),
            #'png': os.path.join(SWFTOOL_BASE, "png2swf.exe"),
            'wav': os.path.join(SWFTOOL_BASE, "wav2swf.exe"),
        }        
        self.UNOCONVTOOL= os.path.join(self.toolbasedir, "tools/unoconv/unoconv")
        self.PDF2TXT = os.path.join(self.toolbasedir, "tools/unoconv/pdf2txt.py")
        self.SPLITPDF = os.path.join(self.toolbasedir, "tools/pdftk/pdftk.exe")
        self.PNGCONVERT= os.path.join(self.toolbasedir, "tools/ImageMagick/convert.exe")

    def getswf(self, fullpath,basedir=None, outputdir=None, convertPdf= False):
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

            cmdpath = self.SWFTOOLS.get(sufix, None)
            apath = ""
            swf_path = fullpath
            if cmdpath == None or sufix=="pdf":
                swf_path = self.convert2pdf(fullpath, os.path.join( outputdir , relate_path ), convertPdf)   
                #fullpath = self.convert2Odf(fullpath, os.path.join( outputdir , relate_path ))   
                self.convert2Png(fullpath, os.path.join( outputdir , relate_path ))   
                fullpath = swf_path
            fullpath = self.convert2swf(swf_path, os.path.join( outputdir , relate_path ))

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
            fullpath = self.convert2pdf(fullpath, os.path.join( outputdir , relate_path ), False)  
            fullpath =   self.convert2txt(fullpath, os.path.join( outputdir , relate_path )) 
            return fullpath
        except Exception, e:
            self.printError()    
                
    def getpdf(self, fullpath,basedir=None, outputdir=None, convertPdf= False):
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
            fullpath = self.convert2pdf(fullpath, os.path.join( outputdir , relate_path ), convertPdf)   
            return fullpath
        except Exception, e:
            self.printError()                

    def getpdfFromRelpath(self, relpath):
        return self.getpdf( os.path.join(self.basedir, path).strip())
    
    def getBookdOutputDir(self, fullpath):
        relate_path = os.path.relpath( fullpath, self.basedir)
        return os.path.join( self.outputdir , relate_path )
        
    def getPdfFilepath(self, fullpath):
        return  os.path.join(self.getBookdOutputDir(fullpath), 'pdf/transfered.pdf')
        
    def getOdfFilepath(self, fullpath):
        return  os.path.join(self.getBookdOutputDir(fullpath), 'odf/transfered.odt')
        
    def getPngFilepath(self, fullpath):
        return  os.path.join(self.getBookdOutputDir(fullpath), 'png/transfered_0000.png')

    def getSwfFilepath(self, fullpath):
        return  os.path.join(self.getBookdOutputDir(fullpath), 'swf/transfered.swf')

    def getTxtFilepath(self, fullpath):
        return  os.path.join(self.getBookdOutputDir(fullpath), 'txt/transfered.txt')
        
    def convert2swf(self,fullpath, todir):
        logging.info("convert %s to swf", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
        swffile = os.path.join(todir, 'swf/transfered.swf')

        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()            
        
        if os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", fullpath)
            return swffile
        elif sufix=="swf":
            if os.path.isfile( swffile ):
                logging.info("Good. File already exists:%s", swffile)
            else:
                shutil.copyfile(fullpath, swffile )     
            return swffile
        
        cmdpath = self.SWFTOOLS.get(sufix, None)
        logging.info('path:%s sufix:%s cmdpath:%s', path, sufix, cmdpath)
        if cmdpath == None:
            return ""
        #ret, logs = self.execmd( r'"%s" "%s" -o "%s"  -T 9 -G' % (cmdpath, fullpath, swffile) )
        ret, logs = self.execmd( r'"%s" "%s" -o "%s"  -T 9' % (cmdpath, fullpath, swffile) )
        if ret:
            return swffile
        else:
            ret, logs = self.execmd( r'"%s" "%s" -o "%s"  -T 9 -G -s poly2bitmap' % (cmdpath, fullpath, swffile) )
            if ret:
                return swffile
            else:
                return ""
    
    def convert2pdf(self,fullpath,todir, convertPdf=False):
        logging.info("convert %s to pdf", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
            
        thisfile = os.path.join(todir, 'pdf/%s.pdf' %(filename) )
        swffile = os.path.join(todir, 'pdf/transfered.pdf' )

        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()  
        if sufix == "pdf" and not convertPdf:                          
            if os.path.isfile( swffile ):
                logging.info("Good. File already exists:%s", swffile)
            else:
                shutil.copyfile(fullpath, swffile )            
        elif os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", swffile)
        else:
            cmdpath = self.UNOCONVTOOL
            port = OfficePortQueue.get()
            os.chdir(os.path.dirname(swffile))
            try:
                pdf_lock.acquire()
                ret, logs = self.execmd( r'python "%s" -f pdf -o . -e Quality=5  -p %s "%s"' % (cmdpath,port, fullpath) )
                OfficePortQueue.put(port)
            except Exception,e:
                OfficePortQueue.put(port+1)
                self.printError()
                return ""
            finally:
                pdf_lock.release()            
                pass
                            
            if ret:
                logging.info( "thisfile:%s    swffile:%s",thisfile,  swffile)
                os.rename(thisfile, swffile)
            else:
                return ""
            
        #now convert to text
        self.convert2txt( swffile, todir)
        
        self.splitPdf(fullpath)
                      
        return swffile
    
    def convert2Png(self,fullpath,todir):
        pdf_path = os.path.join(os.path.dirname(self.getPdfFilepath(fullpath)), "transfered.pdf")
        if not os.path.isfile( pdf_path ):
            logging.error("pdf file is not exist:%s", pdf_path)   
            return ""     
        logging.info("convert %s to png", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
            
        swffile = self.getPngFilepath(fullpath)

        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()  
        
        if sufix == "odt":                          
            if os.path.isfile( swffile ):
                logging.info("Good. File already exists:%s", swffile)
            else:
                shutil.copyfile(fullpath, swffile )    
        elif os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", swffile)
        else:
            #now convert to PNG
            pageNum = self.getPdfPageNum(fullpath)
            swffile = self.getPngFilepath(fullpath)
            outputfile = os.path.join(os.path.dirname(swffile), 'transfered_%04d.png' %(pageNum-1))
            if os.path.isfile(outputfile):
                logging.info("Good. File already exists:%s", outputfile)
                return
                        
            os.chdir(os.path.dirname(swffile))
            cmdpath = self.PNGCONVERT
            try:
                if pageNum <= 50:
                    ret, logs = self.execmd( '"%s" -density 150 "%s" "transfered_%%04d.png"' % (cmdpath,pdf_path) )
                else:
                    ret, logs = self.execmd( '"%s" -density 96 "%s" "transfered_%%04d.png"' % (cmdpath,pdf_path) )                    
            except Exception,e:
                self.printError()
                return ""
            finally:
                pass
                            
            if ret:
                logging.info( "swffile:%s",  swffile)
            else:
                return ""
        return swffile           
         
    def convert2Odf(self,fullpath,todir):
        pdf_path = os.path.join(os.path.dirname(self.getPdfFilepath(fullpath)), "transfered.pdf")
        if not os.path.isfile( pdf_path ):
            logging.error("pdf file is not exist:%s", pdf_path)        
        logging.info("convert %s to odf", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
            
        thisfile = '%s.odt' %(os.path.splitext(pdf_path)[0])    
        swffile = os.path.join(todir, 'odf/transfered.odt' )

        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()  
        
        if sufix == "odt":                          
            if os.path.isfile( swffile ):
                logging.info("Good. File already exists:%s", swffile)
            else:
                shutil.copyfile(fullpath, swffile )    
        elif os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", swffile)
        else:
            cmdpath = self.UNOCONVTOOL
            port = OfficePortQueue.get()
            try:
                pdf_lock.acquire()
                ret, logs = self.execmd( r'python "%s" -f odt -p %s "%s"' % (cmdpath,port, pdf_path) )
                OfficePortQueue.put(port)
            except Exception,e:
                OfficePortQueue.put(port+1)
                self.printError()
                return ""
            finally:
                pdf_lock.release()            
                pass
                            
            if ret:
                logging.info( "thisfile:%s    swffile:%s",thisfile,  swffile)
                try:
                    os.remove(swffile)
                except Exception,e:
                    pass
                os.rename(thisfile, swffile)         
            else:
                return ""
            
        #now convert to text
        self.splitOdf(fullpath)
        
        return swffile        
     
    def convert2txt(self,fullpath,todir):
        logging.info("convert %s to txt", fullpath)
        path = os.path.basename( fullpath)
        fs = os.path.splitext(path)
        filename = fs[0]
        sufix = fs[1][1:].lower().strip()
        swffile = os.path.join(todir, 'txt/transfered.txt')

        if not os.path.isdir( os.path.dirname(swffile) ) :
            try:
                os.makedirs(os.path.dirname(swffile))
            except Exception,e:
                self.printError()            
        
        if os.path.isfile(swffile):
            logging.info("Good. File already exists:%s", fullpath)
            return swffile

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
        else:
            return ""        
            
    def getPdfPageNum(self,fullpath):
        fp = file(self.getPdfFilepath(fullpath), 'rb')
        i = 0
        for page in     PDFPage.get_pages(fp):
            i +=1
        fp.close()        
        logging.debug("page num:%s", i)
        if i >= 5000:
            i = 1
        return i
    
    def splitPdf(self,fullpath, step=10):
        filename = self.getPdfFilepath(fullpath)
        pageNum = self.getPdfPageNum(fullpath)
        pages = (pageNum-1) / step
        outputfile = os.path.join(os.path.dirname(filename), 'transfered_%04d.pdf' %(pages))
        if os.path.isfile(outputfile):
            logging.info("Good. File already exists:%s", outputfile)
            return
        
        os.chdir(os.path.dirname(filename))
        for i in range(pages+1):
            cmdpath = self.SPLITPDF
            try:
                #pdf2txt.py -o output.html samples/naacl06-shinyama.pdf
                #pdftk.exe transfered.pdf cat 1-10 output aaa.pdf
                #outputfile = os.path.join(os.path.dirname(filename), 'transfered_%04d.pdf' %(i))
                outputfile = 'transfered_%04d.pdf' %(i)
                cmd= r'"%s" "%s" cat %s-%s output "%s"' % (cmdpath, os.path.basename(filename), i*step+1, min( (i+1)*step, pageNum ), outputfile)
                ret, logs = self.execmd( cmd )
            except Exception,e:
                self.printError()
                return ""
            finally:
                pass  
                      
    def splitOdf(self, fullpath, step=10):
        p_filename = self.getPdfFilepath(fullpath)
        pageNum = self.getPdfPageNum(fullpath)
        pages = (pageNum-1) / step        
        filename = self.getOdfFilepath(fullpath)
        outputfile = os.path.join(os.path.dirname(filename), 'transfered_%04d.odt' %(pages))
        if os.path.isfile(outputfile):
            logging.info("Good. File already exists:%s", outputfile)
            return
            
        os.chdir(os.path.join( os.path.dirname(filename), ".."))
        for i in range(pages+1):
            cmdpath = self.UNOCONVTOOL
            inputfile = os.path.join( os.path.dirname(p_filename) , 'transfered_%04d.pdf' %(i) )
            if not os.path.isfile(inputfile):
                continue
            port = OfficePortQueue.get()
            try:
                pdf_lock.acquire()
                ret, logs = self.execmd( r'python "%s" -f odt -p %s -o odf "%s"' % (cmdpath,port, inputfile) )
                OfficePortQueue.put(port)
            except Exception,e:
                OfficePortQueue.put(port+1)
                self.printError()
                return ""
            finally:
                pdf_lock.release()            
                pass
                                        
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
            else:
                print 'FAILED!'
                return False, output    
        except Exception,e:
            self.printError()                
            pass
        finally:
            process.kill()                