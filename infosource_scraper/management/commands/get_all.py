from django.core.management.base import NoArgsCommand
from infosource_scraper.scrapers.standard_categories import StandardCategoryScraper
from infosource_scraper.scrapers.departments import DepartmentsScraper

class Command(NoArgsCommand):
    help = 'get all data'
    
    def handle_noargs(self, **options):
        scrapers = [ StandardCategoryScraper(),DepartmentsScraper()]
        for scraper in scrapers:
            scraper.scrape()
        