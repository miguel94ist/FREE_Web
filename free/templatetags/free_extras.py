from django.conf import settings

from django import template

register = template.Library()

@register.simple_tag
def project_name(*args):
    return settings.PROJECT_NAME

@register.simple_tag
def project_acronymum(*args):
    return settings.PROJECT_ACRONYMUN

@register.simple_tag
def site_name (*args):
    return settings.SITE_NAME

