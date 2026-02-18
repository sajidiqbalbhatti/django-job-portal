from django.contrib import admin
from .models import Company

# Register your models here.

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name','country','is_verified','is_active')
    list_filter = ('country','is_verified')
    search_fields = ('name','email')
