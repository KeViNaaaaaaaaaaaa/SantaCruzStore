from django.urls import path
from .views import add_to_cart, remove_from_cart, cart_detail

urlpatterns = [
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('', cart_detail, name='cart_detail'),
]