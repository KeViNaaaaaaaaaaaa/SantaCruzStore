from django.contrib import admin
from apps.catalog.models import Product, Like


admin.site.register(Product)
admin.site.register(Like)