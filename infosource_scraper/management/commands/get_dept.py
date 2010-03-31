from main.models import Department
from infosource_scraper.scrapers.department import DepartmentScraper
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'get a department.  args: a department abbreviation'

    def handle(self, *args, **options):
        abbrev = args[0]
        dept = Department.objects.get(abbrev=abbrev)
        dept_scraper = DepartmentScraper(dept)
        dept_scraper.scrape()