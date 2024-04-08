from django.core.paginator import Paginator
from django.db.models import Sum, F, Prefetch
from django.http import HttpResponse, JsonResponse
import json
from common.models import ShopProducts, Users, Carts, Shops, Admin, Orders, OrderDetails,Followers
from common.models import Products
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages

# Create your views here.
def userpage(request):
    products = ShopProducts.objects.all()
    products2 = Products.objects.all()
    paginator = Paginator(products, 24)  # 假设每页显示多少个商品

    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    u_id = request.session.get('u_id')
    role = request.session.get('role')

    context = {
        'products': paged_products,
        'products2':products2,
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
    user_id = request.POST.get('user_id')
    if user_id is None or user_id == 'None':
        messages.error(request, '请先登录')
        return redirect('login')
    user_id = int(user_id)  # 尝试将 user_id 转换为整数
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
    role = request.session.get('role')
    # 更新数量
    cart.quantity += quantity
    cart.join_time = timezone.now()
    cart.save()
    # 网页跳转问题，如何动态添加，暂时还没想好真的要用javascript吗？
    return render(request, 'productdetails.html', {'product': products, 'products2': products2, 'u_id': user_id, 'role': role})


def userorder(request):
    ord_de=OrderDetails.objects.all()
    u_id = request.session.get('u_id')
    orders=Orders.objects.filter(user_id=u_id)
    order_ids = [order.o_id for order in orders]
    print(order_ids)
    context={
        'orders':orders,
        'ord_de':ord_de,
        'u_id':u_id,
        'order_ids':order_ids
    }
    return render(request,'userorder.html',context)
def userserve(request):
    return render(request,'userserve.html')


def product_details(request, p_id):
    u_id = request.session.get('u_id')
    role = request.session.get('role')
    product = ShopProducts.objects.get(shop_product_id=p_id)
    products2 = Products.objects.get(p_id=product.product_id)

    # 获取该商品所属的店铺
    shop = product.shop

    is_following = False
    if u_id:
        try:
            user = Users.objects.get(u_id=u_id)
            # 检查用户是否关注该店铺
            is_following = Followers.objects.filter(u=user, s=shop).exists()
        except Users.DoesNotExist:
            pass

    return render(request, 'productdetails.html',
                  {'product': product, 'products2': products2, 'u_id': u_id, 'role': role, 'is_following': is_following,
                   'store_name': shop.s_name, 'shop': shop})

def delete_item(request):
    # print(request.body)
    if request.method == 'POST':
        request_data = json.loads(request.body)
        item_id = request_data.get('item_id')
        # print(item_id)
        u_id=request.session.get('u_id')
        cart=Carts.objects.all()
        cart.filter(product_id=item_id,user_id=u_id).delete()
        return JsonResponse({'message': 'Item deleted successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'})


def checkout(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        itemPrices=request_data.get('itemPrices')
        totalPrice=request_data.get('totalPrice')
        itemQuantities=request_data.get('itemQuantities')
        u_id = request.session.get('u_id')
        selected_product_ids = request_data.get('selectedProductIds')
        try:
            # 从购物车表中删除选中的商品
            Carts.objects.filter(product_id__in=selected_product_ids,user_id=u_id).delete()
            i=0
            new_order=Orders.objects.create(
                status='1', paid_time=timezone.localtime(timezone.now())
                ,o_time=timezone.localtime(timezone.now())
                , total_price=totalPrice, user_id=u_id)
            # 在订单表中添加选中的商品
            for product_id in selected_product_ids:
                #shopid未定,orderid未定
                OrderDetails.objects.create(quantity=itemQuantities[i],current_single_price=itemPrices[i],order_id=new_order.o_id,product_id=product_id,shop_id=1)
                i=i+1
            return JsonResponse({'success': True, 'message': '结算成功'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '结算失败'})


def update_quantity(request):
    #有bug，更改数字不可以输入enter键
    if request.method == 'POST':
        request_data = json.loads(request.body)
        cart_id = request_data.get('cart_id')
        new_quantity = request_data.get('newQuantity')
        print(new_quantity)
        try:
            # 更新数据库中对应商品的数量
            product = Carts.objects.get(id=cart_id)
            product.quantity = new_quantity
            product.save()
            return JsonResponse({'success': True, 'message': '数量已更新'})
        except Carts.DoesNotExist:
            return JsonResponse({'success': False, 'message': '商品不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': '更新失败'})

def user_orders(request):
    user_id = request.session.get('u_id')
    try:
        orders = Orders.objects.filter(user_id=user_id).prefetch_related(
            Prefetch('orderdetails_set', queryset=OrderDetails.objects.select_related('order', 'product'))
        )

        orders_data = [{
            'order_id': order.o_id,
            'order_details': [{
                'product_name': Products.objects.get(p_id=detail.product.shop_product_id).p_name,
                'product_image_url': detail.product.product_image_url,
                'quantity': detail.quantity,
                'price': detail.current_single_price,
            } for detail in order.orderdetails_set.all()],
            'total_amount': order.total_price,
            'status': order.status,
            'user_id':order.user_id,
        } for order in orders]

        return JsonResponse({'orders': orders_data})
    except Exception as e:
        print("Error:", e)
        return JsonResponse({'error': 'Failed to retrieve orders'}, status=500)

from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.db import IntegrityError
@require_POST
def follow_shop(request, shop_id):
    shop = get_object_or_404(Shops, pk=shop_id)
    user = get_object_or_404(Users, u_id=request.session.get('u_id'))
    try:
        Followers.objects.create(u=user, s=shop, created_at=timezone.now())
    except IntegrityError:
        pass
    return JsonResponse({'success': True})

@require_POST
def unfollow_shop(request, shop_id):
    shop = get_object_or_404(Shops, pk=shop_id)
    user = get_object_or_404(Users, u_id=request.session.get('u_id'))
    Followers.objects.filter(u=user, s=shop).delete()
    return JsonResponse({'success': True})