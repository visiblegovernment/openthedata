"""
"""

from django.test import TestCase
from infosource_scaper.models import UrlCache
from infosource_scraper.scrapers.department import DepartmentScraper
from main.models import Department

import os

class UrlCacheTest(TestCase):
    test_cachedir = './test/cache/'
    expected_cachefile = './test/cache/http%3A%2F%2Fwww.google.com%2F'

    def setup(self):
        if os.path.existst(self.expected_cachefile):
            os.path.remove(self.expected_cachefile)            
        self.assertEquals(False,os.path.exists(self.expeceted_cachefile))

    def test_get(self):       
        UrlCache.cachedir = self.test_cachedir
        test_cache = UrlCache(path='http://www.google.com/')
        self.assertEquals(self.expected_cachefile,test_cache.cachename())
        str = test_cache.get()
        self.assertEquals(True,os.path.exists(self.expected_cachefile))
        self.assertEquals(str,open(self.expected_cachefile,'r').read())
        
class DepartmentTest(TestCase):
    dept_w_only_standard = Department(name='Asia-Pacific Foundation of Canada',abbrev='apf')
    dept_w_both = Department(name='Agriculture and Agri-Food Canada', abbrev='agr')
    
    def test_resolve_pages(self):
        scraper_w_both = DepartmentScraper(self.dept_w_both)
        self.assertEquals(scraper_w_both.institution_data_page(),'http://infosource.gc.ca/inst/agr/fed05-eng.asp')
        self.assertEquals(scraper_w_both.standard_data_page(),'http://infosource.gc.ca/inst/agr/fed06-eng.asp')
        scraper_w_only_standard = DepartmentScraper(self.dept_w_only_standard)
        self.assertEquals(scraper_w_only_standard.institution_data_page(),None)
        self.assertEquals(scraper_w_only_standard.standard_data_page(),'http://infosource.gc.ca/inst/apf/fed05-eng.asp')
        
