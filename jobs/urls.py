from django.urls import path
from .views import (
    JobListView,
    JobDetailView,
    job_search,
    BulkJobUploadView,
    upload_jobs_csv,
)

app_name = 'jobs'  # Note: matches your redirect in upload_jobs_csv

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
    # Dynamic URLs last
    # -----------------------------
    path('country/<slug:slug>/', JobListView.as_view(), name='jobs_by_country'),  # optional country filter
    path('<slug:slug>/', JobDetailView.as_view(), name='job_detail'),  # dynamic job detail by slug
]
