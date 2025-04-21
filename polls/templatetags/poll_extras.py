from django import template
from mimetypes import guess_type


register = template.Library()

@register.filter(name="get_file_type")
def get_file_type(value):
    return guess_type(value)[0]


@register.filter(name="split")
def split(value, split_by=","):
    return value.split(split_by)


@register.filter(name="split_list")
def split_list(value, split_by=","):
    return [split(val, split_by) for val in value]


@register.filter(name="return_to_percent")
def return_to_percent(value, total=20):
    return round(value / int(total) * 100)
