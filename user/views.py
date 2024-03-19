from django.shortcuts import render, get_object_or_404
from common.models import ShopProducts, Users
from common.models import Products


# Create your views here.
def userspage(request, ID, role):
    # 获取所有商品对象
    products = ShopProducts.objects.all()
    products2 = Products.objects.all()
    # 构建上下文字典
    context = {
        'products': products,
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
    return render(request,'usercart.html')

def product_details(request, p_id):
    product = ShopProducts.objects.get(shop_product_id=p_id)
    products2 = Products.objects.get(p_id=product.product_id)
    return render(request, 'productdetails.html', {'product': product,'products2':products2})