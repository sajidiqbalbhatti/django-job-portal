from django.urls import path
from .views import (
    JobListView,
    JobDetailView,
    job_search,
    BulkJobUploadView,
    upload_jobs_csv,
    JobUpdateView,
    JobDeleteView,
    # CategoryUpdateView,
    # CategoryDeleteView,
    # CompanyUpdateView,
    # CompanyDeleteView,
    # CountryUpdateView,
    # CountryDeleteView,
    # JobTypeUpdateView,
    # JobTypeDeleteView,
)

app_name = 'jobs'

urlpatterns = [
    # -----------------------------
    # Job List (Home)
    # -----------------------------
    path('', JobListView.as_view(), name='job_list'),

    # -----------------------------
    # Static URLs first
    # -----------------------------
    path('bulk-upload/', BulkJobUploadView.as_view(), name='bulk_upload'),
    path('upload-jobs/', upload_jobs_csv, name='upload_jobs_csv'),
    path('search/', job_search, name='job_search'),

    # -----------------------------
    # Dynamic URLs last (Job CRUD)
    # -----------------------------
    path('<slug:slug>/', JobDetailView.as_view(), name='job_detail'),  # job detail
    path('<slug:slug>/edit/', JobUpdateView.as_view(), name='job_edit'),
    path('<slug:slug>/delete/', JobDeleteView.as_view(), name='job_delete'),

    # -----------------------------
    # Category CRUD
    # -----------------------------
    # path('<slug:slug>/edit/', CategoryUpdateView.as_view(), name='category_edit'),
    # path('<slug:slug>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    # # -----------------------------
    # # Company CRUD
    # # -----------------------------
    # path('company/<slug:slug>/edit/', CompanyUpdateView.as_view(), name='company_edit'),
    # path('company/<slug:slug>/delete/', CompanyDeleteView.as_view(), name='company_delete'),

    # # -----------------------------
    # # Country CRUD
    # # -----------------------------
    # path('country/<slug:slug>/', JobListView.as_view(), name='jobs_by_country'),  # optional country filter
    # path('country/<slug:slug>/edit/', CountryUpdateView.as_view(), name='country_edit'),
    # path('country/<slug:slug>/delete/', CountryDeleteView.as_view(), name='country_delete'),

    # # -----------------------------
    # # JobType CRUD
    # # -----------------------------
    # path('jobtype/<slug:slug>/edit/', JobTypeUpdateView.as_view(), name='jobtype_edit'),
    # path('jobtype/<slug:slug>/delete/', JobTypeDeleteView.as_view(), name='jobtype_delete'),
]