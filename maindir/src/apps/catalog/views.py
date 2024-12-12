from datetime import timedelta

from django.shortcuts import render, get_object_or_404
from .models import Product
from apps.orders.models import OrderItem
from django.utils import timezone

def home(request):
    now = timezone.now()
    ten_minutes_ago = now - timedelta(days=7)


    products = Product.objects.all()
    order_item = OrderItem.objects.filter(created_at__range=(ten_minutes_ago, now))
    sell_product = {}
    for i in products:
        sell_product.setdefault(f'{i}|{i.build}', 0)
        for j in order_item:
            if j.product == i and j.product.build == i.build:
                sell_product[f'{i}|{i.build}'] += j.quantity
    sell_product = sorted(sell_product.items(), key=lambda x: (-x[1], x[0]))
    print(sell_product)
    print(products)

    bikes = []
    for product_name_build, _ in sell_product[:4]:
        name, build = product_name_build.split('|')
        print(name)
        print(build)
        product = Product.objects.filter(name=name, build=build).first()
        print(product)
        if product:
            bikes.append(product)
    print(bikes)
    return render(request, 'home.html', {'products': bikes})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.popularity += 1
    product.save()
    return render(request, 'product_detail.html', {'product': product})


def bike_catalog(request):
    profile = request.user.profile
    print(profile)
    products = Product.objects.all()

    # Получаем все уникальные значения для фильтрации
    builds = Product.objects.values_list('build', flat=True).distinct()
    types = Product.objects.values_list('type', flat=True).distinct()
    type_suspensions = Product.objects.values_list('type_suspension', flat=True).distinct()

    # Фильтрация по полям
    selected_builds = request.GET.getlist('build')
    selected_types = request.GET.getlist('type')
    selected_type_suspensions = request.GET.getlist('type_suspension')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort_by = request.GET.get('sort_by')

    if selected_builds:
        products = products.filter(build__in=selected_builds)
    if selected_types:
        products = products.filter(type__in=selected_types)
    if selected_type_suspensions:
        products = products.filter(type_suspension__in=selected_type_suspensions)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Сортировка
    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-popularity')
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    return render(request, 'bike_catalog.html', {
        'products': products,
        'builds': builds,
        'types': types,
        'type_suspensions': type_suspensions,
        'selected_builds': selected_builds,
        'selected_types': selected_types,
        'selected_type_suspensions': selected_type_suspensions,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    })