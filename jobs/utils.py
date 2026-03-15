import xml.etree.ElementTree as ET
from django.utils.text import slugify
from django.utils.html import strip_tags
from jobs.models import Country, Category, Job, Company, JobType
from django.contrib.auth import get_user_model
import uuid

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

    for job_elem in root.findall('Job'):
        try:
            # Required fields mapping
            title = job_elem.findtext('Position')
            company_name = job_elem.findtext('AdvertiserName')
            category_name = job_elem.findtext('Classification')
            country_name = job_elem.findtext('Country')
            description = job_elem.findtext('Description') or ""
            location = job_elem.findtext('Location') or ""
            job_type_name = job_elem.findtext('EmploymentType') or "Full Time"
            apply_url = job_elem.findtext('ApplicationURL') or ""

            # Skip incomplete rows
            if not all([title, company_name, category_name, country_name]):
                skipped += 1
                continue

            # Clean HTML
            description = strip_tags(description)

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

            # JobType normalize
            normalized = job_type_name.lower().replace('-', ' ').replace('_', ' ').strip()
            job_type_name = " ".join(word.capitalize() for word in normalized.split())
            job_type_slug = slugify(job_type_name)

            job_type_obj = jobtype_cache.get(job_type_slug)
            if not job_type_obj:
                job_type_obj = JobType.objects.create(
                    name=job_type_name,
                    slug=job_type_slug
                )
                jobtype_cache[job_type_slug] = job_type_obj

            # Unique slug
            base_slug = slugify(f"{title}-{company_name}-{country_name}")
            job_slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            if job_slug in existing_slugs:
                skipped += 1
                continue

            existing_slugs.add(job_slug)

            # Create job instance with only required fields
            job = Job(
                title=title,
                company=company,
                category=category,
                country=country,
                description=description,
                location=location,
                job_type=job_type_obj,
                apply_url=apply_url,
                slug=job_slug,
                posted_by=default_user,
                is_active=True
            )

            jobs_to_create.append(job)
            added += 1

        except Exception as e:
            errors += 1
            print(f"⚠️ Error processing job: {e}")

    Job.objects.bulk_create(jobs_to_create, batch_size=500)

    return {
        "added": added,
        "skipped": skipped,
        "errors": errors,
        "total_processed": added + skipped + errors
    }