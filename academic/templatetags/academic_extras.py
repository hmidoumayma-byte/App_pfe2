# academic/templatetags/academic_extras.py
from django import template
register = template.Library()

@register.filter
def get(dictionary, key): return dictionary.get(key, [])

@register.filter
def split(value, delimiter=' '): return value.split(delimiter)
