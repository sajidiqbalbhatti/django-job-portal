from django.urls import  path
from core.views import HomeView,AboutPage,PrivacyPolicy



app_name='core'

urlpatterns = [
    
    path('',HomeView.as_view(),name='home'),
    path('about/',AboutPage.as_view(),name='about'),
    path('privacy/',PrivacyPolicy.as_view(),name='privacy'),
]
