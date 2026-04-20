from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

def ads_txt(request):
    return HttpResponse(
        "google.com, pub-3506040482487557, DIRECT, f08c47fec0942fa0",
        content_type="text/plain"
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('job/', include('jobs.urls')),
    path("users/", include("users.urls")),
    path('', include('core.urls')),

    path('ads.txt', ads_txt),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)