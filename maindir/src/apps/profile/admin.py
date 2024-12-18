from django.contrib import admin
from apps.profile.models import Profile, Promocode
from django.utils import timezone



admin.site.register(Profile)


admin.site.register(Promocode)