from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_http_methods, require_POST
import json
from common.models import Admin, Users,Shops,ShopProducts,Orders,OrderDetails,Products
from django.core.paginator import Paginator


def adminpage(request):
    # 如果没有登陆，那么重定向到登陆页面
    if 'ad_id' not in request.session:
        return redirect('login')

    admin = Admin.objects.get(ad_id=request.session['ad_id'])
    users = Users.objects.all()
    shops = Shops.objects.all()
    orders_all = Orders.objects.all()
    order_details = OrderDetails.objects.all()
    products = Products.objects.all()
    shop_products = ShopProducts.objects.all()

    paginator_users = Paginator(users, 6)  # 每页显示 6 个用户
    user_page_number = request.GET.get('user_page')
    user_page_obj = paginator_users.get_page(user_page_number)

    paginator_shops = Paginator(shops, 6)  # 每页显示 6 个商店
    shop_page_number = request.GET.get('shop_page')
    shop_page_obj = paginator_shops.get_page(shop_page_number)

    paginator_products = Paginator(shop_products, 6)  # 每页显示 6 个商品
    product_page_number = request.GET.get('product_page')
    product_page_obj = paginator_products.get_page(product_page_number)

    paginator_orders = Paginator(orders_all, 6)  # 每页显示 6 个订单
    order_page_number = request.GET.get('order_page')
    orders = paginator_orders.get_page(order_page_number)

    context = {
        'admin': admin,
        'is_super': admin.is_super,
        'users': user_page_obj,
        'shops': shop_page_obj,
        'orders': orders,  # 这里只传入当前页的订单
        'order_details': order_details,
        'products': products,
        'shop_products': product_page_obj,
    }
    return render(request, 'adminpage.html', context)


@csrf_exempt
def get_admin_info(request):
    if request.method == 'POST':
        ad_id = request.POST.get('ad_id')
        try:
            admin = Admin.objects.get(ad_id=ad_id)  # 从数据库获取管理员对象
            data = {
              'ad_id': admin.ad_id,
              'ad_acc': admin.ad_acc,
              'ad_psw': admin.ad_psw,
              'is_super': admin.is_super,
            }
            return JsonResponse({'success': True, 'data': data})
        except Admin.DoesNotExist:
            return JsonResponse({'success': False, 'error': '管理员不存在'})
    else:
        return JsonResponse({'success': False, 'error': '无效的请求'})


@require_http_methods(["POST"])
@csrf_exempt
def get_users_info(request):
    # 检查用户ID是否被提交
    user_id = request.POST.get('u_id')
    if not user_id:
        return JsonResponse({'success': False, 'message': '缺少用户ID参数'})

    try:
        # 使用get()查询数据库以获取用户信息
        user = Users.objects.get(u_id=user_id)

        # 返回用户信息
        user_info = {
            'u_id': user.u_id,
            'u_acc': user.u_acc,
            'u_name': user.u_name,
            'u_sex': user.u_sex,
            'u_phone': user.u_phone,
            'email': user.email,
            # 'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')  # 如果需要的话格式化日期
        }
        return JsonResponse({'success': True, 'data': user_info})
    except Users.DoesNotExist:
        # 如果没找到用户，返回错误
        return JsonResponse({'success': False, 'message': '用户不存在'})
    except Exception as e:
        # 捕获其他异常
        return JsonResponse({'success': False, 'message': '服务器错误', 'error': str(e)})


@require_POST  # 确保只接受 POST 请求
@csrf_exempt
def update_user_info(request):
    try:
        data = json.loads(request.body)
        u_id = data.get('u_id')
        u_acc = data.get('u_acc')
        u_name = data.get('u_name')
        u_sex = data.get('u_sex')
        u_phone = data.get('u_phone')
        email = data.get('email')


        # 根据 u_id 查找用户并更新信息
        user = Users.objects.get(u_id=u_id)
        user.u_acc = u_acc
        user.u_name = u_name
        user.u_sex=u_sex
        user.u_phone=u_phone
        user.email=email

        user.save()

        # 返回成功响应
        return JsonResponse({'success': True, 'message': '用户信息已更新'})

    except Users.DoesNotExist:
        # 如果找不到用户
        return JsonResponse({'success': False, 'message': '未找到用户'})
    except json.JSONDecodeError:
        # 如果请求体不是有效的 JSON
        return JsonResponse({'success': False, 'message': '无效的 JSON 数据'})
    except Exception as e:
        # 捕获并处理任何其他异常
        return JsonResponse({'success': False, 'message': '更新过程中出错', 'error': str(e)})

@csrf_exempt
@require_http_methods(["POST"])
def update_shop_info(request):
    try:
        # 解析请求体获取数据
        data = json.loads(request.body)
        s_id = data.get('s_id')
        s_name = data.get('s_name')
        s_acc = data.get('s_acc')
        s_phone = data.get('s_phone')
        email = data.get('email')
        address = data.get('address')

        # 获取要更新的商家对象
        shop = Shops.objects.get(s_id=s_id)

        # 更新商家信息
        shop.s_name = s_name
        shop.s_acc = s_acc
        # shop.s_psw = data.get('s_psw')  # 如果需要更新密码
        shop.s_phone = s_phone
        shop.email = email
        shop.address = address

        # 保存更改
        shop.save()

        # 返回成功响应
        return JsonResponse({'success': True, 'message': '商家信息更新成功'})

    except Shops.DoesNotExist:
        # 如果找不到商家
        return JsonResponse({'success': False, 'message': '商家不存在'})
    except Exception as e:
        # 捕获并响应其他异常
        return JsonResponse({'success': False, 'message': '更新失败', 'error': str(e)})

@require_http_methods(["POST"])
@csrf_exempt
def delete_user(request):
    try:
        data = json.loads(request.body)
        u_id = data['u_id']
        user = Users.objects.get(u_id=u_id)
        user.delete()
        return JsonResponse({'success': True, 'message': '用户已删除'})
    except Users.DoesNotExist:
        return JsonResponse({'success': False, 'message': '用户不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '删除过程出错', 'error': str(e)})

@csrf_exempt
def delete_shop(request):
    try:
        data = json.loads(request.body)
        s_id = data.get('s_id')
        shop = Shops.objects.get(s_id=s_id)
        shop.delete()
        return JsonResponse({'success': True, 'message': '商家删除成功'})

    except Shops.DoesNotExist:
        return JsonResponse({'success': False, 'message': '商家不存在'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': '删除失败: ' + str(e)})

@require_http_methods(["POST"])
@csrf_exempt  # 如果你的前端不处理 CSRF token，可以暂时放宽 CSRF 限制
def get_shop_info(request):
    try:
        # 解析请求体中的 JSON 数据
        data = json.loads(request.body)
        s_id = data.get('s_id')

        # 使用 s_id 查询商家信息
        shop = Shops.objects.get(s_id=s_id)

        # 将商家信息构造成一个字典以便返回
        shop_info = {
            's_id': shop.s_id,
            's_name': shop.s_name,
            's_acc': shop.s_acc,
            's_psw': shop.s_psw,  # 出于安全考虑，通常不应该传输密码
            's_phone': shop.s_phone,
            'email': shop.email,
            'address': shop.address,
        }
        print(shop_info)
        # 返回包含商家信息的 JSON 响应
        return JsonResponse({'success': True, 'data': shop_info})
    except Shops.DoesNotExist:
        # 如果商家不存在，返回错误信息
        return JsonResponse({'success': False, 'message': '商家不存在'})
    except Exception as e:
        # 捕获并处理任何其他异常
        return JsonResponse({'success': False, 'message': '服务器错误', 'error': str(e)})


