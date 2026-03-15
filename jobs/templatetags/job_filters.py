# jobs/templatetags/job_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, key):
    """
    Splits the string by the given key
    Usage: {{ value|split:"<br>" }}
    """
    return value.split(key)
