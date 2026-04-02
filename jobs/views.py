from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import Q
import csv
import uuid

from .models import Job, Category, Country, JobCSVImport, JobType, Company
from .forms import JobCSVImportForm
from .utils import process_xml_jobs


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
                country, _ = Country.objects.get_or_create(name=row['country'].strip())
                category, _ = Category.objects.get_or_create(name=row['category'].strip())
                company, _ = Company.objects.get_or_create(
                    name=row['company'].strip(),
                    defaults={'country': country}
                )
                job_type_name = row.get('job_type', 'Full Time').strip()
                job_type, _ = JobType.objects.get_or_create(name=job_type_name)

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
# Job List with Filters + Pagination
# ===============================
class JobListView(ListView):
    model = Job
    template_name = "job/job_search.html"
    context_object_name = "jobs"
    paginate_by = 20

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True).select_related(
            "company", "category", "country", "job_type"
        ).order_by("-created_at")

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
from django.views.generic import DetailView
from .models import Job

class JobDetailView(DetailView):
    model = Job
    template_name = 'job/job_detail.html'
    context_object_name = 'job'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        """
        Only active jobs, with related foreign key objects
        for optimized queries.
        """
        return Job.objects.filter(is_active=True).select_related(
            'company', 'category', 'country', 'job_type'
        )

    def get_context_data(self, **kwargs):
        """
        Add split description and requirements to context
        so that template can display them as bullet points.
        """
        context = super().get_context_data(**kwargs)
        job = self.object

        # Split by line breaks for bullet lists
        context['description_lines'] = job.description.splitlines() if job.description else []
        context['requirements_lines'] = job.requirements.splitlines() if job.requirements else []

        return context



# ===============================
# Job Search Function
# ===============================

def job_search(request):
    keyword = request.GET.get('q', '').strip()
    location = request.GET.get('location', '').strip()
    job_type_slug = request.GET.get('job_type', '').strip()
    category_slug = request.GET.get('category', '').strip()
    country_slug = request.GET.get('country', '').strip()

    jobs = Job.objects.filter(is_active=True).select_related(
        'company', 'category', 'country', 'job_type'
    )

    # Keyword filter (title, description, company)
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) 
           
        )

    # Location filter (city OR country)
    if location:
        jobs = jobs.filter(
            Q(location__icontains=location) |
            Q(country__name__icontains=location)
        )

    # Job type filter
    if job_type_slug:
        jobs = jobs.filter(job_type__slug__iexact=job_type_slug)

    # Category filter
    if category_slug:
        jobs = jobs.filter(category__slug__iexact=category_slug)

    # Country filter (exact slug match)
    if country_slug:
        jobs = jobs.filter(country__slug__iexact=country_slug)

    # Sort by newest first
    jobs = jobs.order_by('-created_at')

    # Pagination (20 jobs per page)
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




@login_required
def upload_jobs_csv(request):
    """
    Handle job XML/CSV upload and processing.
    - Save uploaded file to JobCSVImport model.
    - Process jobs (create, update, delete) via process_xml_jobs.
    - Display professional success/error messages including duplicates.
    """
    if request.method == 'POST':
        form = JobCSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            # Save uploaded file with 'Pending' status
            obj = form.save(commit=False)
            obj.status = 'Pending'
            obj.save()

            try:
                # Process the uploaded XML/CSV file
                result = process_xml_jobs(obj.file)

                # Update import status
                obj.status = 'Completed'
                obj.save()

                # Build professional message
                msg = (
                    f"✅ {result.get('created', 0)} jobs created. "
                    f"🔄 {result.get('updated', 0)} jobs updated. "
                    f"🗑️ {result.get('deleted', 0)} jobs deleted. "
                    f"⚠️ {result.get('skipped', 0)} skipped. "
                    f"♻️ {result.get('duplicate', 0)} duplicates."
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
# ===============================
# CRUD Views (Slug-based)
# ===============================
# Job CRUD
class JobUpdateView(LoginRequiredMixin, UpdateView):
    model = Job
    fields = [
        'title', 'company', 'description', 'requirements', 'location',
        'job_type', 'category', 'country', 'salary_min', 'salary_max',
        'apply_url', 'is_active'
    ]
    template_name = 'job/job_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('jobs:job_list')


class JobDeleteView(DeleteView):
    model = Job
    template_name = 'job/job_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('jobs:job_list')


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from .utils import process_xml_jobs

@login_required
def fetch_xml_feed(request):
    """
    Fetch XML feed and process it automatically.
    Only logged-in users (admin/staff) can access this.
    """
    try:
        # XML feed URL
        xml_url = 'https://www.jobg8.com/fileserver/jobs.aspx?username=9C69EA0F9C&password=04E077D396&accountnumber=824567&filename=Jobs.zip'
        
        # Call your existing utility function
        result = process_xml_jobs(xml_url)

        # Build professional message
        msg = (
            f"✅ {result.get('created', 0)} jobs created. "
            f"🔄 {result.get('updated', 0)} jobs updated. "
            f"🗑️ {result.get('deleted', 0)} jobs deleted. "
            f"⚠️ {result.get('skipped', 0)} skipped. "
            f"♻️ {result.get('duplicate', 0)} duplicates."
        )
        messages.success(request, msg)

    except Exception as e:
        messages.error(request, f"XML fetch failed: {e}")

    return redirect('core:home')  # ya jis page pe redirect karna chahte ho