import datetime
from django import template
from website.models import UserProfile
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def bounty_total():
    return int(UserProfile.objects.aggregate(Sum('balance'))['balance__sum'])