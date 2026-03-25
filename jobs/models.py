from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
import uuid

User = get_user_model()


# =========================
# COMMON SLUG GENERATOR 🔥
# =========================
def generate_unique_slug(model, value):
    base_slug = slugify(value)
    slug = base_slug
    counter = 1

    while model.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


# =========================
# Category
# =========================
class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# Country
# =========================
class Country(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=5, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Country, self.name)

        if not self.code:
            self.code = self.name[:2].upper()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# Job Type
# =========================
class JobType(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(JobType, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# Company
# =========================
class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="companies")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(Company, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# Job
# =========================
class Job(models.Model):
    external_id = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    location = models.CharField(max_length=200)
    job_type = models.ForeignKey(JobType, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, related_name="jobs")
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    apply_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.title}-{self.company.name}"
            self.slug = f"{slugify(base)}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.company.name}"


# =========================
# CSV Import Tracker
# =========================
class JobCSVImport(models.Model):
    file = models.FileField(upload_to='job_csv/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=100, default='Pending')
    total_jobs = models.IntegerField(default=0)
    created_jobs = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.file.name} ({self.status})"