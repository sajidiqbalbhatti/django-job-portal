from django.urls import path
from .views import (
    JobListView,
    JobDetailView,
    job_search,
    BulkJobUploadView,
    upload_jobs_csv,
    JobUpdateView,
    JobDeleteView,
  
)
from . import views

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
    path('fetch-xml/', views.fetch_xml_feed, name='fetch_xml_feed'),

    # -----------------------------
    # Dynamic URLs last (Job CRUD)
    # -----------------------------
    path('<slug:slug>/', JobDetailView.as_view(), name='job_detail'),  # job detail
    path('<slug:slug>/edit/', JobUpdateView.as_view(), name='job_edit'),
    path('<slug:slug>/delete/', JobDeleteView.as_view(), name='job_delete'),

    # -----------------------------
   
]