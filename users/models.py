from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class  User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('job_seeker','job Seeker'),
        ('employer' ,'Employer'),
        ('admin','Admin')
    )
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES
    )
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    phone = models.CharField(max_length=20, blank=True)
    
    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )
    
    is_verified = models.BooleanField(default=False)
    
    def __ster__(self):
        return self.username

