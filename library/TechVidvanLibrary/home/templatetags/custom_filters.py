from django import template

register = template.Library()

@register.filter
def times(number, default=1):
    return range(number)
