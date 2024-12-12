from django.shortcuts import render, get_object_or_404, redirect
from utils.decoraters import token_required, email_verified_required
from .models import Order, OrderItem, Cart
from apps.catalog.models import Product
from django.contrib.auth.models import User

@email_verified_required
@token_required
def add_to_cart(request, product_id):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=user_obj, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')
@email_verified_required
@token_required
def remove_from_cart(request, cart_item_id):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=user_obj)
    cart_item.delete()
    return redirect('cart_detail')
@email_verified_required
@token_required
def cart_detail(request):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    cart_items = Cart.objects.filter(user=user_obj)
    print(cart_items)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_price': total_price})


@email_verified_required
def create_order(request):
    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return redirect('cart_detail')

        order = Order.objects.create(user=request.user, total_price=0)
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            cart_item.delete()
        order.total_price = sum(item.price for item in order.items.all())
        order.save()
        return redirect('order_detail', order_id=order.id)
    products = Product.objects.all()
    return render(request, 'create_order.html', {'products': products})
@email_verified_required
@token_required
def order_detail(request, order_id):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    order = get_object_or_404(Order, id=order_id, user=user_obj)
    return render(request, 'order_detail.html', {'order': order})
@email_verified_required
@token_required
def order_list(request):
    user = request.user
    user_obj = User.objects.get(id=user['user_id'])
    orders = Order.objects.filter(user=user_obj)
    return render(request, 'order_list.html', {'orders': orders})