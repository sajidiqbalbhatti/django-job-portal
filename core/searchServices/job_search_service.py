from django.db.models import Q
from django.core.paginator import Paginator
from jobs.models import Job


def search_jobs(request, per_page=20):
    keyword = request.GET.get("q", "")
    location = request.GET.get("location", "")
    job_type_slug = request.GET.get("job_type", "")
    category_slug = request.GET.get("category", "")
    country_slug = request.GET.get("country", "")

    jobs = Job.objects.filter(is_active=True).select_related(
        "company", "category", "country", "job_type"
    )

    # 🔎 Keyword Search
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(company__name__icontains=keyword)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if job_type_slug:
        jobs = jobs.filter(job_type__slug__iexact=job_type_slug)

    if category_slug:
        jobs = jobs.filter(category__slug__iexact=category_slug)

    if country_slug:
        jobs = jobs.filter(country__slug__iexact=country_slug)

    jobs = jobs.order_by("-created_at")

    # Pagination
    paginator = Paginator(jobs, per_page)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return {
        "page_obj": page_obj,
        "keyword": keyword,
        "location": location,
        "job_type": job_type_slug,
        "category": category_slug,
        "country": country_slug,
    }
