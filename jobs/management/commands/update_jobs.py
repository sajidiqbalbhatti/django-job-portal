from django.core.management.base import BaseCommand
from jobs.utils import process_xml_jobs

class Command(BaseCommand):
    help = "Fetch live jobs from JobG8 ZIP feed and sync database"

    def handle(self, *args, **kwargs):
        zip_url = "https://www.jobg8.com/fileserver/jobs.aspx?username=9C69EA0F9C&password=04E077D396&accountnumber=824567&filename=Jobs.zip"
        result = process_xml_jobs(zip_url, default_user_username="admin")
        self.stdout.write(f"Jobs Sync Result → {result}")