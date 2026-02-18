# your_app/management/commands/import_jobs_safe.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from jobs.models import Country, Category, Job
from companies.models import Company
import csv

class Command(BaseCommand):
    help = 'Safely import jobs from CSV'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        file_path = kwargs['csv_file']

        with open(file_path, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for row in reader:
                # ---- COUNTRY SAFE ----
                country_name = row['country']
                country, _ = Country.objects.get_or_create(
                    name=country_name,
                    defaults={"slug": slugify(country_name)}
                )

                # ---- CATEGORY SAFE ----
                category_name = row['category']
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={"slug": slugify(category_name)}
                )

                # ---- COMPANY SAFE ----
                company_name = row['company']
                company, _ = Company.objects.get_or_create(
                    name=company_name,
                    defaults={
                        "slug": slugify(company_name),
                        "country": country
                    }
                )

                # ---- JOB CREATE ----
                Job.objects.get_or_create(
                    title=row['title'],
                    company=company,
                    category=category,
                    country=country,
                    defaults={
                        "salary": row.get('salary'),
                        "apply_url": row.get('apply_url'),
                        "job_type": row.get('job_type', 'FT'),
                        "location": row.get('location', '')
                    }
                )

        self.stdout.write(self.style.SUCCESS('Jobs imported successfully!'))
