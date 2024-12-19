from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, F
from django.shortcuts import render
from django.db import models
from apps.orders.models import Order, Product
from django.contrib.auth.models import User

from apps.catalog.models import Like
from apps.orders.models import OrderItem
from apps.profile.models import Promocode

@staff_member_required
def admin_analytics(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    users = User.objects.all()

    products = Product.objects.all()
    likes = Like.objects.all()
    orders = Order.objects.filter(status='Delivered')
    user_obj = User.objects.all()
    orders_pending = Order.objects.filter(status='Pending')
    if start_date and end_date:
        orders = orders.filter(created_at__range=[start_date, end_date])
        products = products.filter(created_at__range=[start_date, end_date])
        orders_pending = orders_pending.filter(created_at__range=[start_date, end_date])
        likes = likes.filter(created_at__range=[start_date, end_date])
        user_obj = user_obj.filter(date_joined__range=[start_date, end_date])


    total_revenue = orders.aggregate(total=Sum('total_price'))['total'] or 0


    total_profit = sum(
        (order.total_price - sum(item.product.cost_price * item.quantity for item in order.items.all()))
        for order in orders
    )


    top_selling_product = OrderItem.objects.filter(order__in=orders) \
        .values('product__name') \
        .annotate(total_sold=Sum('quantity')) \
        .order_by('-total_sold') \
        .first()


    total_likes = likes.count()
    most_liked_product = likes.values('product__name', 'product__build') \
        .annotate(total_likes=Count('id')) \
        .order_by('-total_likes') \
        .first()


    top_liked_products = likes.values('product__name', 'product__build') \
                             .annotate(total_likes=Count('id')) \
                             .order_by('-total_likes')[:5]


    users_with_used_promo = user_obj.filter(
        email__in=Promocode.objects.filter(val_of_activate=0).values_list('email', flat=True)
    ).distinct().count()


    users_with_unused_promo = user_obj.filter(
        email__in=Promocode.objects.filter(val_of_activate=1).values_list('email', flat=True)
    ).distinct().count()


    users_without_promo = user_obj.exclude(email__in=Promocode.objects.values('email')).count()


    used_promocodes = Promocode.objects.filter(val_of_activate=0).count()

    orders_in_pending = orders_pending.filter().count()



    orders_with_used_promo = orders.filter(used_promo=True).count()


    orders_without_promo = orders.filter(used_promo=False).count()


    total_discount = sum(
        sum(item.price * item.quantity for item in order.items.all()) - order.total_price
        for order in orders
        if order.used_promo
    )

    top_profitable_products = OrderItem.objects.filter(order__in=orders) \
                                  .annotate(profit=F('quantity') * (F('product__price') - F('product__cost_price'))) \
                                  .values('product__name') \
                                  .annotate(total_profit=Sum('profit')) \
                                  .order_by('-total_profit')[:5]

    top_selling_products = OrderItem.objects.filter(order__in=orders) \
                               .values('product__name') \
                               .annotate(total_sold=Sum('quantity')) \
                               .order_by('-total_sold')[:5]

    stock_percentages = []
    for product in products:
        sold_quantity = OrderItem.objects.filter(product=product).aggregate(total_sold=Sum('quantity'))[
                            'total_sold'] or 0
        total_quantity = product.val_product + sold_quantity
        if total_quantity > 0:
            percentage = (product.val_product / total_quantity) * 100
        else:
            percentage = 0

        stock_percentages.append({
            'name': product.name,
            'build': product.build,
            'val_product': product.val_product,
            'sold_quantity': sold_quantity,
            'percentage': round(percentage, 2)
        })


    context = {
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'top_profitable_products': top_profitable_products,
        'top_selling_products': top_selling_products,
        'top_selling_product': top_selling_product,
        'stock_percentages': stock_percentages,
        'total_likes': total_likes,
        'most_liked_product': most_liked_product,
        'top_liked_products': top_liked_products,
        'users_with_used_promo': users_with_used_promo,
        'users_with_unused_promo': users_with_unused_promo,
        'users_without_promo': users_without_promo,
        'used_promocodes': used_promocodes,
        'orders_in_pending': orders_in_pending,
        'orders_with_used_promo': orders_with_used_promo,
        'orders_without_promo': orders_without_promo,
        'total_discount': total_discount,
        'start_date': start_date,
        'end_date': end_date,
        'users': users,
    }
    return render(request, 'admin_analytics.html', context)

@staff_member_required
def user_analytics(request, user_id):
    user = request.user
    user_name = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user_name, status='Delivered')

    total_spent = orders.aggregate(total=Sum('total_price'))['total'] or 0
    total_orders = orders.count()

    context = {
        'user': user,
        'user_name': user_name,
        'total_spent': total_spent,
        'total_orders': total_orders,
    }
    return render(request, 'user_analytics.html', context)