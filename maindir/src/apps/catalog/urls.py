from django.urls import path, include
from apps.catalog.views import home, bike_catalog, product_detail, bike_liked


urlpatterns = [
    path('catalog/<int:product_id>/', product_detail, name='product_detail'),
    path('catalog/', bike_catalog, name='bike_catalog'),
    path('liked/', bike_liked, name='bike_liked'),
    path('', home, name='home'),
]