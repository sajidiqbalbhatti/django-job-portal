from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from jobs.models import Job, Category, Country, JobType
from .searchServices.job_search_service import search_jobs


class HomeView(ListView):
    model = Job
    template_name = 'core/home.html'
    context_object_name = 'jobs'
    paginate_by = 30

    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True).select_related(
            'company', 'category', 'country', 'job_type'
        ).order_by('-created_at')

        # Country filter
        country_slug = self.request.GET.get('country')
        if country_slug:
            queryset = queryset.filter(country__slug=country_slug)

        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Job Type filter
        job_type_name = self.request.GET.get('job_type')
        if job_type_name:
            queryset = queryset.filter(job_type__name=job_type_name)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['countries'] = Country.objects.all()
        context['job_types'] = JobType.objects.all()
        context['request'] = self.request
        return context

def job_search(request):
    context = search_jobs(request)

    context.update({
        "categories": Category.objects.all(),
        "countries": Country.objects.all(),
        "job_types": JobType.objects.all(),
    })

    return render(request, "job/job_search.html", context)

class AboutPage(TemplateView):
    template_name = 'core/About.html'

class PrivacyPolicy(TemplateView):
    template_name ="core/privacy_policy.html"