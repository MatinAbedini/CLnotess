from django import template
from mimetypes import guess_type

register = template.Library()

@register.filter(name="get_file_type")
def get_file_type(value):
    """Returns type of the file"""
    return guess_type(value)[0]
