import xml.etree.ElementTree as ET
from django.utils.text import slugify
from jobs.models import Country, Category, Job, Company, JobType
from django.contrib.auth import get_user_model

User = get_user_model()

def process_csv(file, default_user_username='admin'):
    # Default user
    try:
        default_user = User.objects.get(username=default_user_username)
    except User.DoesNotExist:
        default_user = User.objects.first()

    tree = ET.parse(file)
    root = tree.getroot()

    # Cache for faster DB access
    country_cache = {c.name: c for c in Country.objects.all()}
    category_cache = {c.name: c for c in Category.objects.all()}
    company_cache = {c.name: c for c in Company.objects.all()}
    jobtype_cache = {jt.slug: jt for jt in JobType.objects.all()}

    existing_slugs = set(Job.objects.values_list('slug', flat=True))

    jobs_to_create = []
    added = 0
    skipped = 0
    errors = 0

    for job_elem in root.findall('job'):
        try:
            title = job_elem.findtext('title')
            company_name = job_elem.findtext('company')
            category_name = job_elem.findtext('category')
            country_name = job_elem.findtext('country')
            description = job_elem.findtext('description') or ""
            requirements = job_elem.findtext('requirements') or ""
            location = job_elem.findtext('location') or ""
            job_type_name = job_elem.findtext('job_type') or 'Full Time'
            salary_min = job_elem.findtext('salary_min')
            salary_max = job_elem.findtext('salary_max')
            apply_url = job_elem.findtext('apply_url') or ""

            # Skip incomplete rows
            if not all([title, company_name, category_name, country_name]):
                skipped += 1
                continue

            # Country
            country = country_cache.get(country_name)
            if not country:
                country = Country.objects.create(
                    name=country_name,
                    slug=slugify(country_name),
                    code=country_name[:2].upper()
                )
                country_cache[country_name] = country

            # Category
            category = category_cache.get(category_name)
            if not category:
                category = Category.objects.create(
                    name=category_name,
                    slug=slugify(category_name)
                )
                category_cache[category_name] = category

            # Company
            company = company_cache.get(company_name)
            if not company:
                company = Company.objects.create(
                    name=company_name,
                    slug=slugify(company_name),
                    country=country
                )
                company_cache[company_name] = company

            # JobType
            normalized = job_type_name.lower().replace('-', ' ').replace('_', ' ').strip()
            job_type_name = " ".join(word.capitalize() for word in normalized.split())
            job_type_slug = slugify(job_type_name)

            job_type_obj = jobtype_cache.get(job_type_slug)
            if not job_type_obj:
                job_type_obj = JobType.objects.create(name=job_type_name, slug=job_type_slug)
                jobtype_cache[job_type_slug] = job_type_obj

            # Unique slug
            job_slug = slugify(f"{title}-{company_name}-{country_name}")

            # Skip duplicates
            if job_slug in existing_slugs:
                skipped += 1
                continue

            existing_slugs.add(job_slug)

            job = Job(
                title=title,
                company=company,
                category=category,
                country=country,
                description=description,
                requirements=requirements,
                location=location,
                job_type=job_type_obj,
                salary_min=salary_min or None,
                salary_max=salary_max or None,
                apply_url=apply_url,
                slug=job_slug,
                is_active=True
            )

            jobs_to_create.append(job)
            added += 1

        except Exception as e:
            errors += 1
            print(f"⚠️ Error processing job: {e}")

    Job.objects.bulk_create(jobs_to_create, batch_size=500)

    # Return professional stats
    return {"added": added, "skipped": skipped, "errors": errors}
