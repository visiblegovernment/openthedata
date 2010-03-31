from infosource_scraper.scrapers.scraper import Scraper
from infosource_scraper.models import InfoSource 
from main.models import DataCategory,DataSet
from BeautifulSoup import BeautifulSoup
import re

"""
    Scrapes the list of standard data categories.
"""

class StandardCategoryScraper(Scraper):
    
    def __init__(self):
        infosource = InfoSource()
        super(StandardCategoryScraper,self).__init__(infosource.standard_category_page)
        # we have to fix the HTML on this page, otherwise it's a nightmare.
        html = self.cache.get()
        html = re.sub('\r','',html)
        html = re.sub('<strong>([^<]+?)<br />','<strong>\g<1></strong><br />',html)
        html = re.sub('<br />[^<]+?<em>Description:</em></strong>','<br/><strong><em>Description:</em></strong>',html)
        self.soup = BeautifulSoup(html)
        
    def scrape(self):
        categories = self.soup.findAll(id=re.compile("^prn"))
        for category in categories:
            id = category['id']
            name_label = category.findNextSibling('strong')
            desc_label = name_label.findNextSibling('strong')
            desc_end = desc_label.findNextSibling('br')
            next_label = desc_label.findNextSibling('strong')
            name = name_label.contents[0]
            desc_str = unicode('')
            desc_i = desc_label.nextSibling
            while desc_i != desc_end:
                desc_str += unicode(desc_i)
                desc_i = desc_i.nextSibling
            
            cat, g_or_c = DataCategory.objects.get_or_create(name=name,type=DataCategory.STANDARD,desc=desc_str,code=id.upper())

            if re.search('Document Types',str(next_label.contents[0])):
                data_types_str = unicode(next_label.nextSibling)
                DataSet.objects.get_or_create(category=cat,desc=data_types_str)
            else:
                DataSet.objects.get_or_create(category=cat,desc="All Information")
                
