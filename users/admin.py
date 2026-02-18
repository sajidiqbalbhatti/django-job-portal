from django.contrib import admin
from .models import User


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display=('username','email','user_type','is_verified')
    list_filter=('user_type','is_verified')
    search_fields=('username','email')