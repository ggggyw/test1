from django.core.paginator import Paginator
from django.db.models import Sum, F, Prefetch
from django.http import HttpResponse, JsonResponse
import json

from django.views.decorators.csrf import csrf_exempt

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
        }
    return render(request, 'userprofile.html', context)

def edit_userprofile(request):
    context = {}
    u_id = request.session.get('u_id')
    role = request.session.get('role')
    if role == 'user':
        user = get_object_or_404(Users, u_id=u_id)
        if request.method == 'POST':
            # 处理表单提交
            user.u_name = request.POST.get('u_name')
            user.u_psw = request.POST.get('u_psw')
            user.u_sex = request.POST.get('u_sex')
            user.u_phone = request.POST.get('u_phone')
            user.email = request.POST.get('email')
            user.address = request.POST.get('address')
            user.save()
            return redirect('userprofile')
        else:
            # 显示表单
            context = {
                'user': user,
                'role': role,
            }
    return render(request, 'edit_userprofile.html', context)

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
    return render(request, 'productdetails.html', {'product': products, 'products2': products2, 'u_id': user_id, 'role': role})


def userorder(request):
    ord_de=OrderDetails.objects.all()
    u_id = request.session.get('u_id')
    orders=Orders.objects.filter(user_id=u_id)
    order_ids = [order.o_id for order in orders]
    context={
        'orders':orders,
        'ord_de':ord_de,
        'u_id':u_id,
        'order_ids':order_ids
    }
    return render(request,'userorder.html',context)
def userserve(request):
    return render(request,'userserve.html')

from django.db.models import Q
import random

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

    # 获取当前商品的名称
    current_product_name = products2.p_name


    # 使用当前商品名称作为关键字搜索相关商品
    related_products = ShopProducts.objects.filter(
        Q(product__p_name__icontains=current_product_name) |
        Q(product_desc__icontains=current_product_name)
    ).select_related('product', 'shop').exclude(shop_product_id=p_id)

    # 随机选择4个相关商品作为推荐商品
    recommend_products = random.sample(list(related_products), min(8, len(related_products)))


    return render(request, 'productdetails.html',
                  {'product': product, 'products2': products2, 'u_id': u_id, 'role': role,
                   'is_following': is_following, 'store_name': shop.s_name, 'shop': shop,
                   'recommend_products': recommend_products})

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

def checkout(request):#以下内容shopid没有定下来-----------两个时间错乱
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
        # print(new_quantity)
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

#以下再次购买逻辑有问题------------------------------------------------应该根据status决定是否应该再次购买
# --应连同前面一并修改
@csrf_exempt
def again_buy(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        products = data.get('products', [])
        u_id = request.session.get('u_id')
        order = data.get('order', {})
        # print(order)
        new_order = Orders.objects.create(
            status='1', paid_time=timezone.localtime(timezone.now()),
            o_time=timezone.localtime(timezone.now()),
            total_price=order.get('total_price', 0), user_id=u_id)

        for product in products:
            OrderDetails.objects.create(quantity=product.get('quantity', 0),
                                        current_single_price=product.get('price', 0),
                                        order_id=new_order.o_id, product_id=product.get('product_id'), shop_id=1)

        # Return success response
        return JsonResponse({'message': '再次购买成功'}, status=200)
    else:
        # Return error response if request method is not POST
        return JsonResponse({'error': '请求方法不支持'}, status=400)

@csrf_exempt
def delete_order(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        order_id = data.get('order_id', {})
        Orders.objects.filter(o_id=order_id).update(status=5)
        return JsonResponse({'message': '删除成功'}, status=200)
    else:
        return JsonResponse({'error': '删除失败'}, status=400)
def user_orders(request):
    user_id = request.session.get('u_id')
    status = request.GET.get('status')  # 获取 URL 参数中的 status 值
    status_mapping = {
        'all': None,
        'pending': 2,
        'shipped': 3,
        'review': 4,
        'recycle': 5
    }
    # 获取映射后的状态值
    status_value = status_mapping.get(status)
    try:
        # 如果 status_value 为 None，则获取所有订单
        if status_value is None:
            orders = Orders.objects.filter(user_id=user_id).prefetch_related(
                Prefetch('orderdetails_set', queryset=OrderDetails.objects.select_related('order', 'product'))
            )
        else:
            # 根据状态值过滤订单
            orders = Orders.objects.filter(user_id=user_id, status=status_value).prefetch_related(
                Prefetch('orderdetails_set', queryset=OrderDetails.objects.select_related('order', 'product'))
            )

        orders_data = [{
            'order_id': order.o_id,
            'order_details': [{
                'product_name': Products.objects.get(p_id=detail.product.shop_product_id).p_name,
                'product_image_url': detail.product.product_image_url,
                'quantity': detail.quantity,
                'price': detail.current_single_price,
                'product_id':detail.product_id
            } for detail in order.orderdetails_set.all()],
            'total_amount': order.total_price,
            'status': order.status,
            'user_id': order.user_id,
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

def search_products(request):
    query = request.GET.get('q')
    if query:
        products = ShopProducts.objects.filter(
            Q(product__p_name__icontains=query) |
            Q(product_desc__icontains=query)
        ).select_related('product', 'shop')
    else:
        products = ShopProducts.objects.none()

    context = {'products': products, 'query': query}
    return render(request, 'search_results.html', context)


from django.shortcuts import render, redirect, get_object_or_404
from common.models import Users, UserAddresses


def address_management(request):
    user_id = request.session.get('u_id')
    user = get_object_or_404(Users, u_id=user_id)

    default_address = user.address
    other_addresses = UserAddresses.objects.filter(user=user)

    if request.method == 'POST':
        default_address = request.POST.get('default_address')
        user.address = default_address
        user.save()

        for address in other_addresses:
            address_id = address.address_id
            updated_address = request.POST.get(f'address_{address_id}')
            if updated_address:
                address.address = updated_address
                address.save()

        new_address = request.POST.get('new_address')
        if new_address:
            UserAddresses.objects.create(user=user, address=new_address)

        return redirect('address_management')

    context = {
        'default_address': default_address,
        'other_addresses': other_addresses,
    }

    return render(request, 'edit_useradress.html', context)


def set_default_address(request, address_id):
    user_id = request.session.get('u_id')
    user = get_object_or_404(Users, u_id=user_id)

    address = get_object_or_404(UserAddresses, address_id=address_id)

    if user.address:
        UserAddresses.objects.create(user=user, address=user.address)

    user.address = address.address
    user.save()

    address.delete()

    return redirect('address_management')


def delete_address(request, address_id):
    address = get_object_or_404(UserAddresses, address_id=address_id)
    address.delete()

    return redirect('address_management')