from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from .forms import ShopProductForm, ProductForm
from common.models import ShopProducts, ProductCategories, Products, Users, Shops
import pandas as pd
from sqlalchemy import create_engine
from dateutil.relativedelta import relativedelta
from common.models import ShopProducts, ProductCategories, Products, Orders, OrderDetails


# Create your views here.
# 商家页面
def shoppage(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
    paginator = Paginator(shop_products, 3)  # 假设每页显示多少个商品
    products = Products.objects.all()
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    s_id = request.session.get('u_id')
    role = request.session.get('role')

    context = {
        'shop_products': paged_products,
        'products': products,
        's_id': s_id,
        'role': role
    }
    return render(request, 'shoppage.html', context)


def shop_profile(request):
    context = {}
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    if role == 'shop':
        # 获取并处理用户信息
        shop = get_object_or_404(Shops, s_id=s_id)
        context = {
            's_name': shop.s_name,
            's_phone': shop.s_phone,
            'email': shop.email,
            'address': shop.address,
            'role': role,
        }
    return render(request, 'shop_profile.html', context)


def shop_search_products(request):
    query = request.GET.get('query')
    category_id = request.GET.get('category_id', 0)  # 如果没有提供category_id，使用默认值0
    if category_id == 'None':  # 如果category_id的值是'None'，将它设置为0
        category_id = 0
    category_id = int(category_id)  # 确保category_id是一个整数
    page_num = request.GET.get('page')
    s_id = request.session.get('s_id')

    if query is not None and query != '请输入想找的宝贝':
        # 使用 p_id 进行搜索
        if category_id == 0:  # 如果category_id为0，查询所有商品
            ids = Products.objects.filter(
                Q(p_name__icontains=query) |
                Q(brand__icontains=query)
            ).values_list('p_id', flat=True)
        else:  # 否则，查询特定类别的商品
            ids = Products.objects.filter(
                (Q(p_name__icontains=query) |
                 Q(brand__icontains=query)) &
                Q(p_type__category_id=category_id)
            ).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(product_id__in=ids, shop__s_id=s_id)

        paginator = Paginator(shop_products, 2)  # 每页显示12个商品
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            # 如果请求的页码不是整数，返回第一页
            page_obj = paginator.page(1)
        except EmptyPage:
            # 如果请求的页码超出分页器的页数，返回最后一页
            page_obj = paginator.page(paginator.num_pages)
    else:
        if category_id == 0:  # 如果category_id为0，查询所有商品
            shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
            paginator = Paginator(shop_products, 2)
            page = request.GET.get('page', 1)
            page_obj = paginator.get_page(page)
        else:  # 否则，查询特定类别的商品
            shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product__p_type__category_id=category_id)
            paginator = Paginator(shop_products, 2)
            page = request.GET.get('page', 1)
            page_obj = paginator.get_page(page)
    products = Products.objects.all()

    context = {'shop_products': page_obj, 'products': products, 'query': query, 'category_id': category_id}
    return render(request, 'shop_search_results.html', context)


def myproducts(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    # 从GET请求中获取类别ID
    category_id = request.GET.get('category_id')
    if category_id is not None and category_id != '0':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取这个u_id商家的全部商品
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id)

    products = Products.objects.all()

    # 创建一个 Paginator 对象，每页显示 24 个商品
    paginator = Paginator(shop_products, 3)
    # 从 GET 请求的查询参数中获取页码
    page = request.GET.get('page')
    # 使用 Paginator 对象的 get_page 方法来获取当前页的商品
    shop_products = paginator.get_page(page)

    # 检查用户是否已经登录
    if 's_id' in request.session:
        # 如果用户已经登录
        template_name = 'shop_my_products.html'
    else:
        # 如果用户没有登录，就渲染 首页.html 模板
        template_name = '首页.html'

    content = render_to_string(template_name,
                               {'shop_products': shop_products, 'products': products, 'category_id': category_id,
                                'query': None})
    return HttpResponse(content)


def shop_productdetails(request, p_id):
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    shop_product = ShopProducts.objects.get(shop_product_id=p_id)
    products = Products.objects.get(p_id=shop_product.product_id)
    return render(request, 'shop_product_details.html',
                  {'shop_product': shop_product, 'products': products, 's_id': s_id, 'role': role})


def manage_products(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    category_id = request.GET.get('category_id')
    if category_id is not None and category_id != '0' and category_id != '':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取这个u_id商家的全部商品
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
    paginator = Paginator(shop_products, 3)  # 假设每页显示多少个商品
    products = Products.objects.all()
    page = request.GET.get('page')  # 从GET请求的查询参数中获取页码
    paged_products = paginator.get_page(page)  # 获取当前页的商品对象列表

    # 初始化表单实例
    product_form = ProductForm(request.POST or None, request.FILES or None)
    shop_product_form = ShopProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        # 获取当前登录的商家ID
        shop_id = request.session.get('s_id')

        # 验证两个表单是否都有效
        if product_form.is_valid() and shop_product_form.is_valid():
            # 保存Products模型实例
            product = product_form.save()

            # 我们需要为ShopProducts设置外键关系
            # 假设ProductForm的save方法返回新创建的Product实例
            shop_product = shop_product_form.save(commit=False)
            shop_product.product = product
            shop_product.shop_id = shop_id
            if 'product_image' in request.FILES:
                myfile = request.FILES['product_image']
                fs = FileSystemStorage(location='static/商品图片')
                filename = fs.save(myfile.name, myfile)
                shop_product.product_image_url = filename
            # 设置current_price字段的值
            shop_product.current_price = shop_product_form.cleaned_data['current_price']
            # 设置product_auditstatus的值为"待审核"
            shop_product.product_auditstatus = '待审核'
            shop_product.save()

            # 向用户显示成功消息并重定向到商品列表页面
            messages.success(request, '商品已成功添加！')
            return redirect('manage_products')  # 这里假设你有一个商品列表的页面
        else:
            messages.error(request, '添加商品时出现错误。')
    else:
        # GET 请求，创建表单并填充当前模型实例数据
        product_form = ProductForm()
        shop_product_form = ShopProductForm()
    context = {
        'shop_products': paged_products,
        'products': products,
        's_id': s_id,
        'category_id': category_id,
        'product_form': product_form,
        'shop_product_form': shop_product_form,
        'query': None
    }
    return render(request, 'shop_manage_products.html', context)


def shop_search_manage_products(request):
    # 为所有可能的搜索字段获取值
    s_id = request.session.get('s_id')
    product_name = request.GET.get('product_name', '')
    category_id = request.GET.get('category_id', '0')  # 默认为 '0'， 表示所有类别
    brand = request.GET.get('brand', '')
    description = request.GET.get('description', '')
    status = request.GET.get('status', '')
    audit_status = request.GET.get('audit_status', '')
    stock = request.GET.get('stock', '')
    original_price = request.GET.get('original_price', '')
    discount = request.GET.get('discount', '')
    current_price = request.GET.get('current_price', '')

    # 首先获取属于该商家的所有商品
    if s_id is not None:
        queryset = ShopProducts.objects.filter(shop__s_id=s_id)
    else:
        queryset = ShopProducts.objects.none()  # 如果没有s_id，返回空查询集

    # 根据搜索字段过滤查询集，只有输入框有值时才添加到搜索条件
    if product_name:
        queryset = queryset.filter(product__p_name__icontains=product_name)
    if brand:
        queryset = queryset.filter(product__brand__icontains=brand)
    if category_id != '0':  # 如果category_id不是 '0'，则按类别ID过滤
        queryset = queryset.filter(product__p_type__category_id=category_id)
    if description:
        queryset = queryset.filter(product_desc__icontains=description)
    if status:
        queryset = queryset.filter(product_status__iexact=status)
    if audit_status:
        queryset = queryset.filter(product_auditstatus__iexact=audit_status)
    if stock:
        queryset = queryset.filter(stock_quantity__exact=stock)
    if original_price:
        queryset = queryset.filter(original_price__exact=original_price)
    if discount:
        queryset = queryset.filter(discount__exact=discount)
    if current_price:
        queryset = queryset.filter(current_price__exact=current_price)

    # 处理分页逻辑...
    paginator = Paginator(queryset, 2)  # 假设每页显示 10 项商品
    page = request.GET.get('page')
    shop_products = paginator.get_page(page)

    # 将搜索字段回传到模板中，以便保持搜索条件
    context = {
        'shop_products': shop_products,
        'product_name': product_name,
        'category_id': category_id,
        'brand': brand,
        'description': description,
        'status': status,
        'audit_status': audit_status,
        'stock': stock,
        'original_price': original_price,
        'discount': discount,
        'current_price': current_price,
        'query': None
    }

    return render(request, 'shop_manage_products.html', context)


def edit_product(request, product_id):
    shop_product = get_object_or_404(ShopProducts, pk=product_id)
    product = shop_product.product

    if request.method == "POST":
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        shop_product_form = ShopProductForm(request.POST, request.FILES, instance=shop_product)

        if product_form.is_valid() and shop_product_form.is_valid():
            # 更新Products实例
            product_form.save()
            shop_product = shop_product_form.save(commit=False)
            if 'product_image' in request.FILES:
                # 创建一个文件系统存储对象
                fs = FileSystemStorage(location='static/商品图片')
                # 如果已经存在旧的图片，就先删除旧的图片
                if shop_product.product_image_url:
                    fs.delete(shop_product.product_image_url)
                # 保存新的图片
                myfile = request.FILES['product_image']
                filename = fs.save(myfile.name, myfile)
                shop_product.product_image_url = filename
            shop_product.current_price = shop_product_form.cleaned_data['current_price']
            # 设置product_auditstatus的值为"待审核"
            shop_product.product_auditstatus = '待审核'
            shop_product.save()
            # 更新ShopProducts实例
            shop_product_form.save()
            messages.success(request, '修改成功！')
            # 保存后重定向回修改商品页面
            return redirect('edit_product', product_id=product_id)
        else:
            messages.error(request, '修改不成功，请重新修改。')
    else:
        # GET 请求，创建表单并填充当前模型实例数据
        product_form = ProductForm(instance=product)
        shop_product_form = ShopProductForm(instance=shop_product)

    # 将表单传递给模板
    context = {
        'product_form': product_form,
        'shop_product_form': shop_product_form,
        'shop_products': shop_product,
        'query': None
    }
    return render(request, 'shop_edit_product.html', context)


def add_product(request):
    # 初始化表单实例
    product_form = ProductForm(request.POST or None, request.FILES or None)
    shop_product_form = ShopProductForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        # 获取当前登录的商家ID
        shop_id = request.session.get('s_id')

        # 验证两个表单是否都有效
        if product_form.is_valid() and shop_product_form.is_valid():
            # 保存Products模型实例
            product = product_form.save()

            # 我们需要为ShopProducts设置外键关系
            # 假设ProductForm的save方法返回新创建的Product实例
            shop_product = shop_product_form.save(commit=False)
            shop_product.product = product
            shop_product.shop_id = shop_id
            if 'product_image' in request.FILES:
                myfile = request.FILES['product_image']
                fs = FileSystemStorage(location='static/商品图片')
                filename = fs.save(myfile.name, myfile)
                shop_product.product_image_url = filename
            # 设置current_price字段的值
            shop_product.current_price = shop_product_form.cleaned_data['current_price']
            shop_product.save()

            # 向用户显示成功消息并重定向到商品列表页面
            messages.success(request, '商品已成功添加！')
            return redirect('add_product')  # 这里假设你有一个商品列表的页面
        else:
            messages.error(request, '添加商品时出现错误。')
    else:
        # GET 请求，创建表单并填充当前模型实例数据
        product_form = ProductForm()
        shop_product_form = ShopProductForm()

    # 将表单传递给模板
    context = {
        'product_form': product_form,
        'shop_product_form': shop_product_form
    }
    return render(request, 'shop_add_product.html', context)


def delete_product(request, product_id):
    if product_id is not None:
        shop_product = ShopProducts.objects.filter(shop_product_id=product_id).first()
        if shop_product:
            image_path = shop_product.product_image_url  # 获取商品图片的路径
            fs = FileSystemStorage(location='static/商品图片')  # 创建一个文件系统存储对象
            fs.delete(shop_product.product_image_url)  # 删除图片文件
            if fs.exists(shop_product.product_image_url):  # 检查文件是否仍然存在
                print("删除图片错误")  # 如果文件仍然存在，打印一条错误消息
            shop_product.delete()  # 删除对应的商品
    return redirect('manage_products')  # 重定向到manage_products视图


def shop_order(request):
    # 从会话中获取当前登录的商家ID
    shop_id = request.session.get('s_id')

    # 查询这个商家的所有订单
    order_ids = OrderDetails.objects.filter(shop__s_id=shop_id).values_list('order__o_id', flat=True)
    orders = Orders.objects.filter(o_id__in=order_ids)

    # 将订单传递给模板
    context = {
        'orders': orders,
        'query': None
    }
    return render(request, 'shop_order.html', context)


def user_detail(request, user_id):
    user = get_object_or_404(Users, pk=user_id)
    data = {
        'u_name': user.u_name,
        'u_sex': user.u_sex,
        'u_address': user.address,
        'u_email': user.email,
        'u_phone': user.u_phone,
    }
    return JsonResponse(data)


def product_detail(request, p_id):
    # 根据 p_id 获取 ShopProducts 实例
    shop_product = get_object_or_404(ShopProducts, pk=p_id)
    # 从相关联的 Products 实例中获取产品信息
    product = shop_product.product
    data = {
        'p_name': product.p_name,
        'p_type': product.p_type.category_name,  # 假设 ProductCategories 有一个 'category_name' 字段
        'brand': product.brand,
        'current_price': shop_product.current_price,
        'product_desc': shop_product.product_desc,
        'product_status': shop_product.product_status,
        'stock_quantity': shop_product.stock_quantity,
        'original_price': shop_product.original_price,
        'discount': shop_product.discount,
        'product_image_url': shop_product.product_image_url,
        'query': None
    }

    # 返回 JSON 形式的响应
    return JsonResponse(data)


def ship_product(request, o_id):
    if request.method == 'POST':
        try:
            # 在数据库中查找订单实例
            order = Orders.objects.get(o_id=o_id)
            # 检查订单状态是否为"待发货"
            if order.status == '待发货':
                # 修改订单状态为"待收货"
                order.status = '待收货'
                # 保存更改
                order.save()
                # 返回一个成功的响应
                return JsonResponse({'success': True, 'new_status': '待收货'})
            else:
                # 如果订单状态不允许发货，则返回一个错误响应
                return JsonResponse({'success': False, 'error': 'Invalid order status for shipment'})
        except Orders.DoesNotExist:
            # 订单不存在时的错误响应
            return JsonResponse({'success': False, 'error': 'Order does not exist'})
        except Exception as e:
            # 捕获其它异常，返回一个错误信息
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        # 对于非POST请求，返回一个错误响应
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def rfm_analysis(request):
    engine = create_engine('mysql+pymysql://web:dzh20030112@47.93.125.169/web')
    products_data = pd.read_sql_query('select * from products', engine)
    orders_data = pd.read_sql_query("select * from orders", engine)
    order_details_data = pd.read_sql_query("select * from order_details", engine)

    # 转换时间类型
    orders_data['o_time'] = pd.to_datetime(orders_data['o_time'])
    orders_data['paid_time'] = pd.to_datetime(orders_data['paid_time'])
    # 将表融合
    merged_data = pd.merge(orders_data, order_details_data, left_on='o_id', right_on='order_id')
    merged_data = pd.merge(merged_data, products_data, left_on='product_id', right_on='p_id')

    merged_data.head(1)

    # 筛选出一年之内的购买记录
    current_time = pd.Timestamp.now()
    two_years_ago = current_time - relativedelta(years=1)
    filtered_data = merged_data[(merged_data['paid_time'] >= two_years_ago) &
                                (merged_data['paid_time'] <= current_time)]

    shop_id = request.session.get('s_id')
    filtered_data = filtered_data.query(f'shop_id == {shop_id}')
    filtered_data.head(1)

    # 创建一个空的DataFrame来存储RFM值
    RFM = pd.DataFrame()
    # 计算R（最近一次购买时间）注意，这个R是dataframe格式
    R = filtered_data.groupby('user_id')['paid_time'].max().reset_index()
    R.columns = ['u_id', 'last_purchase_time']  # 重命名列以避免混淆
    RFM['u_id'] = R['u_id']
    RFM['Recency'] = (pd.Timestamp.now() - R['last_purchase_time']).dt.days
    # 计算F（购买频次）
    F = filtered_data.groupby('user_id').size().reset_index(name='frequency')
    # 使用size()来计算每个组的行数,即该u_id在这一段时间内共出现了多少次。
    RFM['Frequency'] = F['frequency']
    # 计算M（总消费金额）
    M = filtered_data.groupby('user_id')['total_price'].sum().reset_index()
    RFM['Monetary'] = M['total_price']

    R_threshold = RFM['Recency'].mean()
    F_threshold = RFM['Frequency'].mean()
    M_threshold = RFM['Monetary'].mean()
    print(R_threshold)
    print(F_threshold)
    print(M_threshold)

    # 标识高于(1)或低于(0)平均值
    RFM['R'] = (RFM['Recency'] < R_threshold).astype(int)
    RFM['F'] = (RFM['Frequency'] > F_threshold).astype(int)
    RFM['M'] = (RFM['Monetary'] > M_threshold).astype(int)

    RFM['RFM_Class'] = RFM['R'].astype(str) + RFM['F'].astype(str) + RFM['M'].astype(str)

    # 创建中文标签映射
    rfm_labels = {
        '111': '重要价值客户',
        '110': '潜力客户',
        '101': '重要深耕客户',
        '100': '新客户',
        '011': '重要唤回客户',
        '010': '一般维持用户',
        '001': '重要挽留客户',
        '000': '流失用户'
    }

    RFM['RFM_Label'] = RFM['RFM_Class'].map(rfm_labels)

    RFM_data = RFM[['u_id', 'Recency', 'Frequency', 'Monetary', 'RFM_Class', 'RFM_Label']].to_dict(orient='records')

    # 创建一个字典，其中包含您想要在模板中使用的数据
    context = {
        'RFM_data': RFM_data,
        # 如果您还有其他数据需要传递，可以在这里添加
    }

    # 渲染模板，并将上下文传递给模板
    return render(request, 'rfm.html', context)
