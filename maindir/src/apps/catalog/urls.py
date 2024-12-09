from django.urls import path, include
from apps.catalog.views import home, bike_catalog, product_detail


urlpatterns = [
    path('catalog/<int:product_id>/', product_detail, name='product_detail'),
    path('catalog/', bike_catalog, name='bike_catalog'),
    path('', home, name='home'),
]