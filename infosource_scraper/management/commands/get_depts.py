from django.core.management.base import NoArgsCommand
from infosource_scraper.scrapers.departments import DepartmentsScraper

class Command(NoArgsCommand):
    help = 'get all departments'
    
    def handle_noargs(self, **options):
        scraper = DepartmentsScraper()
        scraper.scrape(False)
        