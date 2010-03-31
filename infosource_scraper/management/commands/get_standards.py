from django.core.management.base import NoArgsCommand
from infosource_scraper.scrapers.standard_categories import StandardCategoryScraper

class Command(NoArgsCommand):
    help = 'get all standard categories'
    
    def handle_noargs(self, **options):
        scraper = StandardCategoryScraper()
        scraper.scrape()
        