from tkinter.font import names

from django.shortcuts import render, get_object_or_404, redirect
from utils.decoraters import token_required, email_verified_required
from .models import Order, OrderItem, Cart
from apps.catalog.models import Product
from apps.profile.models import Promocode
from django.contrib.auth.models import User


@email_verified_required
@token_required
def add_to_cart(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart_detail')


@email_verified_required
@token_required
def remove_from_cart(request, cart_item_id):
    user = request.user
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=user)
    cart_item.delete()
    return redirect('cart_detail')


@email_verified_required
@token_required
def cart_detail(request):
    user = request.user

    cart_items = Cart.objects.filter(user=user)
    total_price = round(sum(item.product.price * item.quantity for item in cart_items), 2)

    promocode = request.GET.get('promocode')
    request.session['promo_valid'] = False
    print(user.email)
    try:
        promo = Promocode.objects.get(email=user.email)
        print(promocode, promo.promocode)
        if promocode == promo.promocode and promo.val_of_activate == 1:
            total_price = round((total_price * 90 / 100), 2)
            request.session['promo_valid'] = True
            print('dsdsdsdfsdsdfsdfsdfsdsdfsdfsd')
    except Promocode.DoesNotExist:
        pass
    if request.method == 'POST':
        if not cart_items:
            return redirect('cart_detail')

        order = Order.objects.create(user=user, total_price=total_price)
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            bike = Product.objects.get(name=cart_item.product.name, build=cart_item.product.build)
            bike.val_product -= cart_item.quantity
            bike.save()
            cart_item.delete()
        order.total_price = sum(item.price for item in order.items.all())

        if request.session['promo_valid']:
            order.used_promo = True
            promo.val_of_activate = 0
            order.total_price = round((order.total_price * 90 / 100), 2)
            del request.session['promo_valid']

        order.save()
        promo.save()
        return redirect('order_detail', order_id=order.id)
    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'user': user, 'total_price': total_price})
