from django.shortcuts import render, redirect
from django.contrib import messages
from common.models import Admin, Users,Shops,ShopProducts,Orders,OrderDetails,Products
from django.core.paginator import Paginator

def adminpage(request):
    if 'ad_id' not in request.session:
        return redirect('login')

    admin = Admin.objects.get(ad_id=request.session['ad_id'])
    users = Users.objects.all()
    paginator = Paginator(users, 6)  # 每页显示 6 个用户
    page_number = request.GET.get('user_page')
    page_obj = paginator.get_page(page_number)
    shops = Shops.objects.all()
    shop_paginator = Paginator(shops, 6)  # 每页显示 6 个商店
    shop_page_number = request.GET.get('shop_page')
    shop_page_obj = shop_paginator.get_page(shop_page_number)
    context = {
        'admin': admin,
        'is_super': admin.is_super,
        'users': page_obj,
        'shops': shop_page_obj,
        'orders': Orders.objects.all(),
        'order_details': OrderDetails.objects.all(),
        'products': Products.objects.all(),
        'shop_products': ShopProducts.objects.all(),
    }
    return render(request, 'adminpage.html', context)