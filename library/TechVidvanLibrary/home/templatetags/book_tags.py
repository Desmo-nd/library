from django import template

register = template.Library()

@register.filter
def make_star_range(value):
    return range(int(value))

@register.filter
def make_star_range_diff(value):
    return range(5 - int(value))
