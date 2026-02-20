from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from django.db.models import Q
import csv
from .utils import process_csv



from jobs.models import Job, Category, Country, JobCSVImport, JobType, Company
from .forms import JobCSVImportForm



# ===============================
# Bulk CSV Upload (Professional)
# ===============================
class BulkJobUploadView(View):
    template_name = 'job/bulk_upload.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        csv_file = request.FILES.get('csv_file')

        if not csv_file:
            messages.error(request, "No CSV file selected!")
            return redirect('jobs:bulk_upload')

        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.DictReader(decoded_file)

        jobs_to_create = []
        row_count = 0

        for row in reader:
            row_count += 1
            try:
                # ✅ Auto create or fetch FK
                country, _ = Country.objects.get_or_create(name=row['country'].strip())
                category, _ = Category.objects.get_or_create(name=row['category'].strip())
                company, _ = Company.objects.get_or_create(
                    name=row['company'].strip(),
                    defaults={'country': country}
                )
                job_type_name = row.get('job_type', 'Full Time').strip()
                job_type, _ = JobType.objects.get_or_create(name=job_type_name)

                # ✅ Convert salary to int if present
                salary_min = int(row['salary_min']) if row.get('salary_min') else None
                salary_max = int(row['salary_max']) if row.get('salary_max') else None

                job = Job(
                    title=row['title'].strip(),
                    company=company,
                    description=row.get('description', '').strip(),
                    requirements=row.get('requirements', '').strip(),
                    location=row.get('location', '').strip(),
                    job_type=job_type,
                    category=category,
                    country=country,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    apply_url=row.get('apply_url', '').strip(),
                    is_active=True
                )
                jobs_to_create.append(job)

            except Exception as e:
                print(f"Row {row_count} error: {e}")

        if jobs_to_create:
            Job.objects.bulk_create(jobs_to_create)
            messages.success(request, f"{len(jobs_to_create)} jobs imported successfully!")
        else:
            messages.warning(request, "No jobs imported. Check CSV.")

        return redirect('jobs:bulk_upload')


# ===============================
# Job List
# ===============================
from django.views.generic import ListView
from .models import Job, Category, Country, JobType


class JobListView(ListView):
    model = Job
    template_name = "job/job_search.html"
    context_object_name = "jobs"
    paginate_by = 20

    def get_queryset(self):
        queryset = (
            Job.objects.filter(is_active=True)
            .select_related("company", "category", "country", "job_type")
            .order_by("-created_at")
        )

        # GET filters
        country = self.request.GET.get("country")
        category = self.request.GET.get("category")
        job_type = self.request.GET.get("job_type")
        keyword = self.request.GET.get("keyword")

        if country:
            queryset = queryset.filter(country__slug=country)

        if category:
            queryset = queryset.filter(category__slug=category)

        if job_type:
            queryset = queryset.filter(job_type__slug=job_type)

        if keyword:
            queryset = queryset.filter(title__icontains=keyword)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["countries"] = Country.objects.all()
        context["job_types"] = JobType.objects.all()
        return context



# ===============================
# Job Detail
# ===============================
class JobDetailView(DetailView):
    model = Job
    template_name = 'job/job_detail.html'
    context_object_name = 'job'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Job.objects.filter(is_active=True).select_related(
            'company', 'category', 'country', 'job_type'
        )


# ===============================
# Job Search (Professional)
# ===============================
from django.core.paginator import Paginator
from django.db.models import Q

def job_search(request):
    keyword = request.GET.get('q', '')
    location = request.GET.get('location', '')
    job_type_slug = request.GET.get('job_type', '')
    category_slug = request.GET.get('category', '')
    country_slug = request.GET.get('country', '')

    jobs = Job.objects.filter(is_active=True).select_related(
        'company', 'category', 'country', 'job_type'
    )

    # 🔎 Keyword Search
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(company__name__icontains=keyword)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    if job_type_slug:
        jobs = jobs.filter(job_type__slug__iexact=job_type_slug)

    if category_slug:
        jobs = jobs.filter(category__slug__iexact=category_slug)

    if country_slug:
        jobs = jobs.filter(country__slug__iexact=country_slug)

    # ✅ Order + Pagination
    jobs = jobs.order_by('-created_at')
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'keyword': keyword,
        'location': location,
        'job_type': job_type_slug,
        'category': category_slug,
        'country': country_slug,
        'categories': Category.objects.all(),
        'countries': Country.objects.all(),
        'job_types': JobType.objects.all(),
    }

    return render(request, 'job/job_search.html', context)


# ===============================
# CSV Upload (Form Based)
# ===============================
from django.contrib import messages

def upload_jobs_csv(request):
    if request.method == 'POST':
        form = JobCSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save()
            try:
                result = process_csv(obj.file)

                obj.status = 'Completed'
                obj.save()

                # Professional message
                msg = (
                    f"✅ {result['added']} jobs imported successfully. "
                    f"⚠️ {result['skipped']} duplicates skipped. "
                    f"❌ {result['errors']} errors."
                )
                messages.success(request, msg)

            except Exception as e:
                obj.status = 'Failed'
                obj.save()
                messages.error(request, f"Import failed: {e}")

            return redirect('jobs:upload_jobs_csv')
    else:
        form = JobCSVImportForm()

    return render(request, 'job/upload_csv.html', {'form': form})

