from django.db import models
import urllib
import os

"""
    Simple local file cache for a given URL.
"""

class UrlCache(models.Model):

    cachedir = "./data/cache/"
    path = models.URLField()
    
    def cachename(self):
        slugged_name = urllib.quote(self.path,'')
        return( self.cachedir + slugged_name )
        
    def date(self):
        return( os.path.getmtime(self.cachename()) )
        
    def get(self, expires = None):
        if not os.path.exists(self.cachename()):
            fp = urllib.urlopen(self.path)
            op = open(self.cachename(), "wb")
            s = fp.read()
            op.write(s)
            fp.close()
            op.close()
        ip = open(self.cachename(),'r')
        return( ip.read() )
     

class InfoSource(object):
    department_list_page = 'http://infosource.gc.ca/fed/fed07-eng.asp'
    standard_category_page = 'http://infosource.gc.ca/fed/fed04-eng.asp'
    
    def department_index(self,department):
        return( self.department_page(department,'fed00-eng.asp') )
        
    def department_page(self, department,page):
        return( "http://infosource.gc.ca/inst/%s/%s" % (department.abbrev,page) )
            