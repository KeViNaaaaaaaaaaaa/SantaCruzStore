from datetime import timedelta
from math import trunc

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Like
from apps.orders.models import OrderItem
from django.utils import timezone
from django.contrib.auth.models import User

from utils.decoraters import token_required
from django.contrib.auth.models import AnonymousUser

from apps.profile.models import Profile


def home(request):
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)

    products = Product.objects.all()
    order_item = OrderItem.objects.filter(created_at__range=(seven_days_ago, now))
    sell_product = {}
    for i in products:
        sell_product.setdefault(f'{i}|{i.build}', 0)
        for j in order_item:
            if j.product == i and j.product.build == i.build:
                sell_product[f'{i}|{i.build}'] += j.quantity
    sell_product = sorted(sell_product.items(), key=lambda x: (-x[1], x[0]))

    bikes = []
    for product_name_build, _ in sell_product[:4]:
        name, build = product_name_build.split('|')
        product = Product.objects.filter(name=name, build=build).first()
        if product:
            bikes.append(product)
    return render(request, 'home.html', {'products': bikes})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.popularity += 1
    product.save()
    return render(request, 'product_detail.html',
                  {'product': product})


def bike_catalog(request):
    # if isinstance(request.user, AnonymousUser):
    #     pass
    # else:

    products = Product.objects.all()
    user_true = False
    try:
        user = request.user
        u = []
        is_liked = Like.objects.filter(user=user)
        for i in is_liked:
            u.append(i.product)
        user_true = True
    except:
        pass
    if request.method == 'POST':
        if user_true:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            like, created = Like.objects.get_or_create(user=user, product=product)
            if not created:
                like.delete()
            return redirect('bike_catalog')

    builds = Product.objects.values_list('build', flat=True).distinct()
    types = Product.objects.values_list('type', flat=True).distinct()
    type_suspensions = Product.objects.values_list('type_suspension', flat=True).distinct()

    name = request.GET.get('name')
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
    if name:
        products = products.filter(name__icontains=name)

    if sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'popular':
        products = products.order_by('-popularity')
    elif sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')

    paginator = Paginator(products, 8)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

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
        'is_liked': u if user_true else None,
    })

@token_required
def bike_liked(request):
    user = request.user
    print(user)
    is_liked = Like.objects.filter(user=user)
    print(is_liked)

    # if request.method == 'POST':
    #     if request.user.is_authenticated:
    #         if is_liked:
    #             Like.objects.filter(user=request.user, product=product).delete()
    #         else:
    #             Like.objects.create(user=request.user, product=product)
    #         return redirect('product_detail')
    #     else:
    #         return redirect('login')
    #
    return render(request, 'liked_bikes.html', {'is_liked': is_liked, 'user': user})
