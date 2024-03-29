from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from common.models import ShopProducts, Users, Carts, Shops, Admin
from common.models import Products
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.utils import timezone


# Create your views here.
def userpage(request):
    products = ShopProducts.objects.all()
    paginator = Paginator(products, 24)  # 假设每页显示多少个商品

    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    u_id = request.session.get('u_id')
    role = request.session.get('role')

    context = {
        'products': paged_products,
        'user_id': u_id,
        'role': role
    }
    return render(request, 'userpage.html', context)


def userprofile(request):
    context = {}
    u_id = request.session.get('u_id')
    role = request.session.get('role')
    if role == 'user':
        # 获取并处理用户信息
        user = get_object_or_404(Users, u_id=u_id)
        context = {
            'u_id': user.u_id,
            'u_acc': user.u_acc,
            'u_name': user.u_name,
            'u_psw': user.u_psw,
            'u_sex': user.u_sex,
            'u_phone': user.u_phone,
            'email': user.email,
            'address': user.address,
            'created_at': user.created_at,
            'role': role,
             # 添加更多需要的用户信息字段
        }
    elif role == 'shop':
        # 获取并处理商户信息
        shop = get_object_or_404(Shops, s_id=u_id)
        context = {
            's_id': shop.s_id,
            's_name': shop.s_name,
            's_acc': shop.s_acc,
            's_psw': shop.s_psw,
            's_phone': shop.s_phone,
            'email': shop.email,
            'address': shop.address,
            'role': role,
            # 添加更多需要的商户信息字段
        }

    elif role == 'admin':
        # 获取并处理管理员信息
        admin = get_object_or_404(Admin, ad_id=u_id)  # 假设你的管理员模型名为Admin
        context = {
            'ad_id': admin.ad_id,
            'ad_acc': admin.ad_acc,
            'ad_psw': admin.ad_psw,
            'is_super': admin.is_super,
            'role': role,
            # 添加更多需要的管理员信息字段
        }
    else:
        return HttpResponse('Invalid role.')  # 或者你可以选择重定向到错误页面
    return render(request, 'userprofile.html', context)

def usercart(request):
    cart=Carts.objects.all()
    shopproduct=ShopProducts.objects.all()
    product=Products.objects.all()
    u_id = request.session.get('u_id')
    context={
        'cart': cart,
        'shoppro':shopproduct,
        'pro':product,
        'uid':u_id
    }
    return render(request,'usercart.html',context)


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    user_id=request.POST.get('user_id')
    products = ShopProducts.objects.filter(product_id=product_id).first()
    products2 = Products.objects.filter(p_id=product_id).first()
    quantity = int(request.POST.get('quantity', 1))
    shop_id=products.shop_id

    # 获取或创建购物车项
    cart, created = Carts.objects.get_or_create(
        product_id=product_id,
        user_id=user_id,
        shop_id=shop_id,
        defaults={'quantity': 0,
                  'join_time':'2023-03-19 00:00'}
    )

    # 更新数量
    cart.quantity += quantity
    cart.join_time = timezone.now()
    cart.save()
    # 网页跳转问题，如何动态添加，暂时还没想好真的要用javascript吗？
    return render(request,'productdetails.html',{'product': products,'products2':products2})

def userorder(request):
    return render(request,'userorder.html')
def userserve(request):
    return render(request,'userserve.html')
def product_details(request, p_id):
    u_id= request.session.get('u_id')
    role= request.session.get('role')
    product = ShopProducts.objects.get(shop_product_id=p_id)
    products2 = Products.objects.get(p_id=product.product_id)
    return render(request, 'productdetails.html', {'product': product,'products2':products2,'u_id':u_id,'role':role})