from infosource_scraper.models import UrlCache
from BeautifulSoup import BeautifulSoup

"""  Scraper base class.  Uses beautiful soup as default parser.
"""

class Scraper(object):
    
    def __init__(self, url):
        self.cache = UrlCache(path=url)
        self.soup = BeautifulSoup(self.cache.get(),convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        
 