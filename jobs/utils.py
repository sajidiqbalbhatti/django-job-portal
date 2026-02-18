from django.utils.text import slugify
from jobs.models import Country, Category, Job, Company, JobType
from django.contrib.auth import get_user_model

User = get_user_model()


def process_csv(file, default_user_username='admin'):
    import csv

    # Default user
    try:
        default_user = User.objects.get(username=default_user_username)
    except User.DoesNotExist:
        default_user = User.objects.first()

    # Read CSV
    decoded = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded)

    # CSV header mapping
    header_map = {
        'title': ['title', 'job title', 'job_title'],
        'company': ['company', 'company name', 'employer'],
        'category': ['category', 'job category'],
        'country': ['country', 'country name'],
        'description': ['description', 'job description'],
        'requirements': ['requirements', 'skills'],
        'location': ['location', 'job location'],
        'job_type': ['job_type', 'type', 'employment_type'],
        'salary_min': ['salary_min', 'min salary'],
        'salary_max': ['salary_max', 'max salary'],
        'apply_url': ['apply_url', 'url']
    }

    def get_value(row, key):
        """Get value from row with multiple header aliases"""
        for alias in header_map.get(key, []):
            if alias in row:
                return (row.get(alias) or '').strip()
        return ''

    job_count = 0

    for row_num, raw_row in enumerate(reader, start=1):
        row = {k.strip().lower(): (v or '').strip() for k, v in raw_row.items()}

        title = get_value(row, 'title')
        company_name = get_value(row, 'company')
        category_name = get_value(row, 'category')
        country_name = get_value(row, 'country')

        # Skip incomplete rows
        if not all([title, company_name, category_name, country_name]):
            print(f"⚠️ Skipping row {row_num}: Missing required fields -> {row}")
            continue

        # ForeignKeys
        country, _ = Country.objects.get_or_create(
            name=country_name,
            defaults={'slug': slugify(country_name), 'code': country_name[:2].upper()}
        )
        category, _ = Category.objects.get_or_create(
            name=category_name,
            defaults={'slug': slugify(category_name)}
        )
        company, _ = Company.objects.get_or_create(
            name=company_name,
            defaults={'slug': slugify(company_name), 'country': country}
        )

        # JobType - safe slug without random -1 suffix
        job_type_name = get_value(row, 'job_type') or 'Full Time'
        slug = slugify(job_type_name)
        job_type_obj = JobType.objects.filter(slug=slug).first()
        if not job_type_obj:
            job_type_obj = JobType.objects.create(name=job_type_name, slug=slug)

        # Create Job
        Job.objects.create(
            title=title,
            company=company,
            category=category,
            country=country,
            description=get_value(row, 'description'),
            requirements=get_value(row, 'requirements'),
            location=get_value(row, 'location'),
            job_type=job_type_obj,
            salary_min=get_value(row, 'salary_min') or None,
            salary_max=get_value(row, 'salary_max') or None,
            apply_url=get_value(row, 'apply_url'),
            is_active=True
        )

        print(f"✅ Job Created: {title} at {company_name}")
        job_count += 1

    print(f"\n🎉 CSV Import Complete: {job_count} jobs added.")
