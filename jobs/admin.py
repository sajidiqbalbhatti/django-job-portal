from django.contrib import admin
from .models import Job, Category, Country,JobCSVImport,Company,JobType


admin.site.register(Category)
admin.site.register(Country)
admin.site.register(Company)
admin.site.register(JobType)

admin.site.register(JobCSVImport)
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    # Admin list columns
    list_display = (
        'title',
        'company',
        'job_type',
        'country',
        'category',
        'location',
        'salary_min',
        'salary_max',
        'is_active',
        'created_at',
    )

    # Search bar
    search_fields = (
        'title',
        'company__name',
        'category__name',
        'country__name',
        'location',
    )

    # Right filters
    list_filter = ('category', 'country', 'job_type', 'is_active')

    # Inline edit
    list_editable = ('is_active',)

    # Pagination
    list_per_page = 20

    # Readonly auto fields
    readonly_fields = ('created_at', 'updated_at')

    # Form sections
    fieldsets = (
        ('Job Basic Info', {
            'fields': ('title', 'company', 'posted_by')
        }),
        ('Job Description', {
            'fields': ('description', 'requirements')
        }),
        ('Job Details', {
            'fields': ('category', 'country', 'location', 'job_type')
        }),
        ('Salary', {
            'fields': ('salary_min', 'salary_max')
        }),
        ('Apply & Status', {
            'fields': ('apply_url', 'is_active')
        }),
        ('System Info', {
            'fields': ('created_at', 'updated_at')
        }),
    )
