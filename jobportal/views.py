from django.http import HttpResponse
def ads_txt(request):
    return HttpResponse(
        "google.com, pub-3506040482487557, DIRECT, f08c47fec0942fa0",
        content_type="text/plain"
    )