from django.urls import path
from .views import add_to_cart, remove_from_cart, cart_detail, create_order, order_detail, order_list

urlpatterns = [
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/', cart_detail, name='cart_detail'),
    path('create/', create_order, name='create_order'),
    path('<int:order_id>/', order_detail, name='order_detail'),
    path('', order_list, name='order_list'),
]