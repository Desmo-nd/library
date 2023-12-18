from django import template
from django.contrib.auth.hashers import check_password

register = template.Library()

@register.filter
def compare_passwords(password1, password2):
    return check_password(password1, password2)