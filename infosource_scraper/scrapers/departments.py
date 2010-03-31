from infosource_scraper.scrapers.department import DepartmentScraper
from infosource_scraper.scrapers.scraper import Scraper
from main.models import Department
from infosource_scraper.models import InfoSource
import re

"""
    Scrape the full list of departments with ATIP-able information.
"""

class DepartmentsScraper(Scraper):
    
    def __init__(self):
        super(DepartmentsScraper,self).__init__(InfoSource.department_list_page)
        
    def scrape(self,scrape_depts=True):
        links = self.soup.findAll(href=re.compile("/inst/.../fed00-eng.asp"))
        for link in links:
            match = re.search("/inst/(...)/fed00-eng.asp",link['href'])
            abbrev = match.group(1)
            name = link.contents[0]
            name = re.sub('\s*See\s+','',name)
            dept,g_or_c = Department.objects.get_or_create(name=name,abbrev=abbrev)
            if scrape_depts:
                dept_scraper = DepartmentScraper(dept)
                dept_scraper.scrape()
