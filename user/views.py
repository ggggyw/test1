from django.shortcuts import render, get_object_or_404
from common.models import ShopProducts, Users, Carts
from common.models import Products
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.utils import timezone


# Create your views here.
def userspage(request, ID, role):
    # 获取所有商品对象
    shop_products = ShopProducts.objects.all()
    products2 = Products.objects.all()
    # 构建上下文字典
    context = {
        'shop_products': shop_products,
        'products2': products2,
        'user_id': ID,
        'role': role
    }
    # 根据角色重定向到不同的页面
    if role == 'user':
        return render(request, 'userspage.html', context)
    elif role == 'admin':
        return render(request, 'adminpage.html', context)
    elif role == 'shop':
        return render(request, 'shoppage.html', context)
    else:
        # 如果角色不匹配，可以重定向到一个通用页面或显示错误信息
        return render(request, 'errorpage.html', {'message': '无效的角色'})


def userprofile(request, ID):
    # 使用 get_object_or_404 来获取用户对象，如果用户不存在则返回404错误
    user = get_object_or_404(Users, u_id=ID)

    # 构建上下文字典，包含用户信息
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
        # 添加更多需要的用户信息字段
    }

    # 将上下文字典传递给模板
    return render(request, 'userprofile.html', context)


def usercart(request):
    return render(request, 'usercart.html')


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    user_id = request.POST.get('user_id')
    products = ShopProducts.objects.filter(product_id=product_id).first()
    products2 = Products.objects.filter(p_id=product_id).first()
    quantity = int(request.POST.get('quantity', 1))
    shop_id = products.shop_id

    # 获取或创建购物车项
    cart, created = Carts.objects.get_or_create(
        product_id=product_id,
        user_id=user_id,
        shop_id=shop_id,
        defaults={'quantity': 0,
                  'join_time': '2023-03-19 00:00'}
    )

    # 更新数量
    cart.quantity += quantity
    cart.join_time = timezone.now()
    cart.save()
    # 网页跳转问题，如何动态添加，暂时还没想好真的要用javascript吗？
    return render(request, 'productdetails.html', {'product': products, 'products2': products2})


def userorder(request):
    return render(request, 'userorder.html')


def userserve(request):
    return render(request, 'userserve.html')


def product_details(request, p_id, u_id):
    product = ShopProducts.objects.get(shop_product_id=p_id)
    products2 = Products.objects.get(p_id=product.product_id)
    u_id = Users.objects.get(u_id=u_id)
    return render(request, 'productdetails.html', {'product': product, 'products2': products2, 'u_id': u_id})
