import xml.etree.ElementTree as ET
import requests
import zipfile
import io
from django.utils.text import slugify
from django.db import transaction
from jobs.models import Country, Category, Job, Company, JobType
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


def fetch_xml_from_zip(zip_url):
    """
    Download ZIP from URL and return XML content as bytes.
    """
    try:
        response = requests.get(zip_url, timeout=20)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for filename in z.namelist():
                if filename.endswith(".xml"):
                    with z.open(filename) as xml_file:
                        return xml_file.read()
        logger.error("No XML file found inside ZIP!")
        return None
    except Exception as e:
        logger.error(f"Failed to download or read ZIP: {e}")
        return None


def process_xml_jobs(zip_url, default_user_username="admin"):
    """
    Fetch jobs from JobG8 ZIP feed, extract XML, and sync with the database.
    Creates, updates, and deletes jobs automatically.
    """
    # =========================
    # DEFAULT USER
    # =========================
    default_user = User.objects.filter(username=default_user_username).first() or User.objects.first()
    if not default_user:
        raise Exception("No user found in database!")

    # =========================
    # FETCH XML FROM ZIP
    # =========================
    xml_content = fetch_xml_from_zip(zip_url)
    if not xml_content:
        return {"error": "Failed to fetch XML from ZIP"}

    try:
        root = ET.fromstring(xml_content)
    except Exception as e:
        logger.error(f"XML Parse Error: {e}")
        return {"error": "Failed to parse XML"}

    # =========================
    # CACHES (OPTIMIZED)
    # =========================
    country_cache = {c.name.lower(): c for c in Country.objects.all()}
    category_cache = {c.name.lower(): c for c in Category.objects.all()}
    company_cache = {c.name.lower(): c for c in Company.objects.all()}
    jobtype_cache = {jt.slug: jt for jt in JobType.objects.all()}

    existing_jobs = {
        j.external_id: j
        for j in Job.objects.select_related("company", "category", "country", "job_type")
    }

    xml_ids = set()
    created = 0
    updated = 0
    skipped = 0
    duplicate = 0

    # =========================
    # MAIN TRANSACTION
    # =========================
    with transaction.atomic():
        for job_elem in root.findall("Job"):

            # UNIQUE ID
            external_id = (job_elem.findtext("SenderReference") or "").strip()
            if not external_id:
                skipped += 1
                continue

            # duplicate inside XML
            if external_id in xml_ids:
                duplicate += 1
                continue

            xml_ids.add(external_id)

            # =========================
            # EXTRACT DATA
            # =========================
            title = (job_elem.findtext("Position") or "").strip()
            if not title:
                skipped += 1
                continue

            company_name = (job_elem.findtext("AdvertiserName") or "Unknown").strip()
            category_name = (job_elem.findtext("Classification") or "General").strip()
            country_name = (job_elem.findtext("Country") or "Unknown").strip()
            description = job_elem.findtext("Description") or ""  # keep HTML
            location = (job_elem.findtext("Location") or "").strip()
            job_type_name = (job_elem.findtext("EmploymentType") or "Full Time").strip()
            apply_url = (job_elem.findtext("ApplicationURL") or "").strip()

            # =========================
            # COUNTRY
            # =========================
            country_key = country_name.lower()
            country = country_cache.get(country_key)
            if not country:
                country = Country.objects.create(name=country_name, slug=slugify(country_name))
                country_cache[country_key] = country

            # =========================
            # CATEGORY
            # =========================
            category_key = category_name.lower()
            category = category_cache.get(category_key)
            if not category:
                category = Category.objects.create(name=category_name, slug=slugify(category_name))
                category_cache[category_key] = category

            # =========================
            # COMPANY
            # =========================
            company_key = company_name.lower()
            company = company_cache.get(company_key)
            if not company:
                company = Company.objects.create(name=company_name, slug=slugify(company_name), country=country)
                company_cache[company_key] = company

            # =========================
            # JOB TYPE
            # =========================
            job_type_slug = slugify(job_type_name.lower())
            job_type = jobtype_cache.get(job_type_slug)
            if not job_type:
                job_type = JobType.objects.create(name=job_type_name, slug=job_type_slug)
                jobtype_cache[job_type_slug] = job_type

            # =========================
            # CREATE / UPDATE
            # =========================
            job_obj = existing_jobs.get(external_id)
            if job_obj:
                # UPDATE only if changed
                if (
                    job_obj.title != title or
                    job_obj.description != description or
                    job_obj.location != location or
                    job_obj.company_id != company.id or
                    job_obj.category_id != category.id or
                    job_obj.country_id != country.id or
                    job_obj.job_type_id != job_type.id or
                    job_obj.apply_url != apply_url
                ):
                    job_obj.title = title
                    job_obj.description = description
                    job_obj.location = location
                    job_obj.company = company
                    job_obj.category = category
                    job_obj.country = country
                    job_obj.job_type = job_type
                    job_obj.apply_url = apply_url
                    job_obj.save()
                    updated += 1
                else:
                    duplicate += 1
            else:
                # CREATE
                slug = f"{slugify(title)[:50]}-{external_id}"
                Job.objects.create(
                    external_id=external_id,
                    title=title,
                    company=company,
                    category=category,
                    country=country,
                    description=description,
                    location=location,
                    job_type=job_type,
                    apply_url=apply_url,
                    slug=slug,
                    posted_by=default_user,
                    is_active=True
                )
                created += 1

        # =========================
        # SAFE DELETE
        # =========================
        if xml_ids:
            deleted, _ = Job.objects.exclude(external_id__in=xml_ids).delete()
        else:
            deleted = 0

    # =========================
    # LOGGING
    # =========================
    logger.info(
        f"Jobs Sync → Created: {created}, Updated: {updated}, Deleted: {deleted}, Skipped: {skipped}, Duplicate: {duplicate}"
    )

    return {
        "created": created,
        "updated": updated,
        "deleted": deleted,
        "skipped": skipped,
        "duplicate": duplicate
    }