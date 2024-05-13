from datetime import datetime, timedelta

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Count, Sum, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDay, TruncDate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils import timezone

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
    # 从GET请求中获取查询和类别ID
    category_id = request.GET.get('category_id', 0)
    if category_id == 'None':
        category_id = 0
    category_id = int(category_id)

    # 基于category_id来过滤shop_product
    if category_id:
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product__p_type__category_id=category_id)
    else:
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id)

    # 分页器
    paginator = Paginator(shop_products, 8)  # 每页显示 8 个商品
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 根据类别统计订单的各个状态的数量
    # 调用函数获取订单状态统计
    order_status_counts = get_order_status_counts(s_id, category_id)

    # 使用函数统计商品审核状态的数量
    audit_status_counts = get_product_audit_status_counts(shop_products)

    # 使用函数统计商品状态的数量
    product_status_counts = get_product_status_counts(shop_products)

    # 获取今天的日期
    today_date = timezone.now().date()
    today_date_str = today_date.strftime('%Y-%m-%d')
    # --------------------------------------------------商品卡片信息----------------------------------------
    # 获取一周前的日期
    start_date = timezone.now().date() - timedelta(days=7)
    # 获取今天的日期
    today = timezone.now().date()
    # 使用函数获取销量最高的商品信息
    top_selling_product_info = get_top_selling_product_info(s_id, category_id)
    # 使用函数获取当天销量最高的商品信息
    today_top_selling_product_info = get_today_top_selling_product_info(s_id, category_id)
    # 一周内销量最高的商品信息
    weekly_top_selling_product_info = get_weekly_top_selling_product_info(s_id, start_date, today_date, category_id)

    # --------------------------------------------------商品卡片信息----------------------------------------
    # 调用统计函数获取相应的数据
    # 获取指定商店、指定类别的已售出商品总数
    total_sold = get_sold_products_count(s_id, category_id if category_id != 0 else None)
    # 获取指定商店、指定类别的总收入
    total_revenue = get_total_revenue(s_id, category_id if category_id != 0 else None)
    # 获取当前日期
    today_date = timezone.now().date()
    # 获取当前日期的订单数
    today_orders = get_today_orders_count(s_id, today_date, category_id if category_id != 0 else None)
    # 获取当前日期已售出商品的数量
    today_product_sales = get_today_sold_products_count(s_id, today_date, category_id if category_id != 0 else None)
    # 获取当前日期的总收入
    total_revenue_today = get_today_total_revenue(s_id, today_date, category_id if category_id != 0 else None)

    # --------------------------------------------------图表信息----------------------------------------
    # 统计过去七天的数据
    # 调用定义的函数获取过去七天每天的订单数量统计
    daily_orders_count = get_daily_orders_count(s_id, category_id)
    # 调用定义的函数获取过去七天每天的销售商品数量统计
    daily_sales_products_count = get_daily_sales_products_count(s_id, category_id)
    # 调用定义的函数获取过去七天每天的营业额统计
    daily_revenue = get_daily_revenue(s_id, category_id)
    # 创建一个包含最近七天的日期列表
    seven_days_dates = [(timezone.now().date() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]
    # 创建一部字典，将日期作为键，对应的数据作为值
    daily_orders_dict = {sale['date'].strftime("%m-%d"): sale['count'] for sale in daily_orders_count}
    daily_sales_dict = {sale['date'].strftime("%m-%d"): sale['quantity_sum'] for sale in daily_sales_products_count}
    daily_revenue_dict = {sale['date'].strftime("%m-%d"): "{:.2f}".format(sale['total_income']) for sale in
                          daily_revenue}

    # 根据日期列表创建新列表，如果某一天没有数据，值即为0
    daily_orders_list = [[date, daily_orders_dict.get(date, 0)] for date in seven_days_dates]
    daily_sales_list = [[date, daily_sales_dict.get(date, 0)] for date in seven_days_dates]
    daily_revenue_list = [[date, daily_revenue_dict.get(date, '0.00')] for date in seven_days_dates]

    # --------------------------------------------------图表信息----------------------------------------

    # 拼接上下文信息
    context = {
        'shop_products': page_obj,
        'query': None,
        'today_date_str': today_date_str,
        'category_id': category_id,
        'order_status_counts': order_status_counts,
        'product_audit_status_counts': audit_status_counts,
        'product_status_counts': product_status_counts,
        'sold_products_count': total_sold,
        'top_selling_product_info': top_selling_product_info if (
                top_selling_product_info and top_selling_product_info != 0) else None,
        'today_top_selling_product_info': today_top_selling_product_info if today_top_selling_product_info else None,
        'total_revenue': total_revenue,
        'today_orders': today_orders,
        'today_product_sales': today_product_sales,
        'total_revenue_today': total_revenue_today,
        'weekly_top_selling_product_info': weekly_top_selling_product_info if weekly_top_selling_product_info else None,
        'daily_orders_list': daily_orders_list,
        'daily_sales_list': daily_sales_list,
        'daily_revenue_list': daily_revenue_list,
        'daily_orders_count': daily_orders_count,
    }

    return render(request, 'shoppage.html', context)


def get_product_audit_status_counts(shop_products):
    """
       根据提供的商品查询集来统计商品的审核状态数量。
       参数:
       shop_products -- 商品的查询集
       返回:
       一个字典，键是商品审核状态，值是对应的数量。
       """
    product_audit_status_counts = shop_products.values('product_auditstatus').annotate(
        count=Count('product_auditstatus'))
    audit_status_counts = dict(product_audit_status_counts.values_list('product_auditstatus', 'count'))

    return audit_status_counts


def get_product_status_counts(shop_products):
    """
    根据提供的商品查询集来统计商品的状态数量。
    参数:
    shop_products -- 商品的查询集
    返回:
    一个字典，键是商品状态，值是对应的数量。
    """
    product_status_counts = shop_products.values('product_status').annotate(
        count=Count('product_status'))
    status_counts_dict = dict(product_status_counts.values_list('product_status', 'count'))

    return status_counts_dict


def get_top_selling_product_info(s_id, category_id=None):
    """
    根据提供的商家ID和可选的商品类别ID，获取销量最高的商品信息。
    参数:
    s_id -- 商家ID
    category_id -- 商品类别ID (默认为 None，此时不过滤类别)
    返回:
    销量最高的商品对象或None
    """
    # 定义订单状态列表
    valid_statuses = ['待发货', '待收货', '已收货', '已完成']
    # 如果提供了category_id，则过滤对应类别下的商品
    if category_id:
        top_selling_product_info = ShopProducts.objects.filter(
            shop__s_id=s_id,
            product__p_type__category_id=category_id,
            orderdetails__order__status__in=valid_statuses
        ).annotate(
            quantity_sold=Sum('orderdetails__quantity')
        ).order_by('-quantity_sold').first()
    else:
        top_selling_product_info = ShopProducts.objects.filter(
            shop__s_id=s_id,
            orderdetails__order__status__in=valid_statuses
        ).annotate(
            quantity_sold=Sum('orderdetails__quantity')
        ).order_by('-quantity_sold').first()
    if top_selling_product_info:
        top_selling_product_info.discount = top_selling_product_info.discount * 100
    return top_selling_product_info


def get_today_top_selling_product_info(s_id, category_id=None):
    """
    获取指定商家当天销量最高的商品信息，可选的类别ID筛选商品。
    参数:
    s_id -- 商家ID
    category_id -- 商品类别ID (默认为None，此时不过滤类别)
    today -- 代表当天日期的对象
    返回:
    当天销量最高的商品对象或None
    """
    today = timezone.now().date()
    valid_statuses = ['待发货', '待收货', '已收货', '已完成']
    if category_id:
        today_top_selling_product_info = ShopProducts.objects.filter(
            shop__s_id=s_id,
            product__p_type__category_id=category_id,
            orderdetails__order__o_time__date=today,
            orderdetails__order__status__in=valid_statuses
        ).annotate(
            quantity_sold=Sum('orderdetails__quantity')
        ).order_by('-quantity_sold').first()
    else:
        today_top_selling_product_info = ShopProducts.objects.filter(
            shop__s_id=s_id,
            orderdetails__order__o_time__date=today,
            orderdetails__order__status__in=valid_statuses
        ).annotate(
            quantity_sold=Sum('orderdetails__quantity')
        ).order_by('-quantity_sold').first()
    if today_top_selling_product_info:
        today_top_selling_product_info.discount = today_top_selling_product_info.discount * 100
    return today_top_selling_product_info


def get_weekly_top_selling_product_info(s_id, start_date, today_date, category_id=None):
    """
    根据商家ID和可选的商品类别ID获取一周内销量最高的商品信息。
    参数:
    s_id -- 商家ID
    start_date -- 周的开始日期
    today_date -- 周的结束日期（通常是今天的日期）
    category_id -- 商品类别ID (默认为None，此时不过滤类别)
    返回:
    一周内销量最高的商品对象或None
    """
    valid_statuses = ['待发货', '待收货', '已收货', '已完成']
    query_filters = {
        'shop__s_id': s_id,
        'orderdetails__order__o_time__date__range': (start_date, today_date),
        'orderdetails__order__status__in': valid_statuses
    }
    if category_id:
        query_filters['product__p_type__category_id'] = category_id

    weekly_top_selling_product_info = (
        ShopProducts.objects.filter(**query_filters)
        .annotate(quantity_sold=Sum('orderdetails__quantity'))
        .order_by('-quantity_sold')
        .first()
    )
    # 将折扣转换为百分数，如果有折扣字段的话
    if weekly_top_selling_product_info and hasattr(weekly_top_selling_product_info, 'discount'):
        weekly_top_selling_product_info.discount_percentage = weekly_top_selling_product_info.discount * 100

    return weekly_top_selling_product_info


def get_sold_products_count(s_id, category_id=None):
    """获取指定商家下指定类别的已售出商品总数"""
    filters = {
        'order__status__in': ['待发货', '待收货', '已收货', '已完成'],
        'shop__s_id': s_id
    }
    if category_id:
        filters['product__product__p_type__category_id'] = category_id

    result = OrderDetails.objects.filter(**filters).aggregate(total_sold=Sum('quantity'))

    total_sold = result['total_sold'] if result['total_sold'] is not None else 0
    return total_sold


def get_total_revenue(s_id, category_id=None):
    """获取指定商家下指定类别的总收入"""
    order_statuses_for_revenue = ['已完成', '已收货']
    filters = {
        'order__status__in': order_statuses_for_revenue,
        'shop__s_id': s_id
    }
    if category_id:
        filters['product__product__p_type__category_id'] = category_id

    result = OrderDetails.objects.filter(**filters).aggregate(total_income=Sum('order__total_price'))
    total_income = round(result['total_income'], 2) if result['total_income'] is not None else 0
    return total_income


def get_today_total_revenue(s_id, today_date, category_id=None):
    """获取今日指定商家下指定类别的总收入"""
    order_statuses_for_revenue = ['已完成', '已收货']
    filters = {
        'order__status__in': order_statuses_for_revenue,
        'shop__s_id': s_id,
        'order__o_time__date': today_date
    }
    if category_id:
        filters['product__product__p_type__category_id'] = category_id

    result = OrderDetails.objects.filter(**filters).aggregate(total_income_today=Sum('order__total_price'))
    total_income_today = round(result['total_income_today'], 2) if result['total_income_today'] is not None else 0
    return total_income_today


def get_today_orders_count(s_id, today_date, category_id=None):
    """获取今日指定商家下指定类别的订单总数"""
    filters = {
        'orderdetails__shop__s_id': s_id,
        'o_time__date': today_date
    }
    if category_id:
        filters['orderdetails__product__product__p_type__category_id'] = category_id

    return Orders.objects.filter(**filters).count()


def get_today_sold_products_count(s_id, today_date, category_id=None):
    """获取今日指定商家下指定类别的售出商品总数"""
    filters = {
        'order__status__in': ['待发货', '待收货', '已收货', '已完成'],
        'shop__s_id': s_id,
        'order__o_time__date': today_date
    }
    if category_id:
        filters['product__product__p_type__category_id'] = category_id

    result = OrderDetails.objects.filter(**filters).aggregate(total_sold_today=Sum('quantity'))
    total_sold_today = result['total_sold_today'] if result['total_sold_today'] is not None else 0
    return total_sold_today


def get_daily_orders_count(s_id, category_id=None):
    """
    获取过去七天每天的订单数量
    """
    seven_days_ago = timezone.now().date() - timedelta(days=6)
    order_statuses = ['待发货', '待收货', '已收货', '已完成']

    filters = {
        'orderdetails__shop__s_id': s_id,
        'o_time__date__gte': seven_days_ago,
        'status__in': order_statuses
    }
    if category_id:
        filters['orderdetails__product__product__p_type__category_id'] = category_id

    daily_orders_count = Orders.objects.filter(**filters).annotate(
        date=TruncDate('o_time')
    ).values('date').annotate(count=Count('o_id')).values('date', 'count').order_by('date')

    return daily_orders_count


def get_daily_sales_products_count(s_id, category_id=None):
    """
    获取过去七天每天销售的商品数量
    """
    seven_days_ago = timezone.now().date() - timedelta(days=6)
    order_statuses = ['待发货', '待收货', '已收货', '已完成']

    filters = {
        'shop__s_id': s_id,
        'order__o_time__date__gte': seven_days_ago,
        'order__status__in': order_statuses
    }
    if category_id:
        filters['product__product__p_type__category_id'] = category_id

    daily_sales_products_count = OrderDetails.objects.filter(**filters).annotate(
        date=TruncDate('order__o_time')
    ).values('date').annotate(quantity_sum=Sum('quantity')).values('date', 'quantity_sum').order_by('date')

    return daily_sales_products_count


def get_daily_revenue(s_id, category_id=None):
    """
    获取过去七天每天的营业额
    """
    seven_days_ago = timezone.now().date() - timedelta(days=6)
    order_statuses_for_revenue = ['已完成', '已收货']

    filters = {
        'shop__s_id': s_id,
        'order__o_time__date__gte': seven_days_ago,
        'order__status__in': order_statuses_for_revenue
    }
    if category_id:
        filters['product__product__p_type__category_id'] = category_id

    daily_revenue = OrderDetails.objects.filter(**filters).annotate(
        date=TruncDate('order__o_time')
    ).values('date').annotate(
        total_income=ExpressionWrapper(
            Sum('order__total_price'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).values('date', 'total_income').order_by('date')

    return daily_revenue


def get_order_status_counts(s_id, category_id=None):
    """
    根据商家ID和可选的类别ID来统计订单的各个状态的数量。

    参数:
    s_id -- 商家ID
    category_id -- 类别ID (默认为 None，表示不按类别筛选)

    返回:
    一个字典，键是订单状态，值是对应的数量。
    """
    if category_id:
        orders_within_category = Orders.objects.filter(
            orderdetails__product__product__p_type__category_id=category_id,
            orderdetails__shop__s_id=s_id
        )
    else:
        orders_within_category = Orders.objects.filter(orderdetails__shop__s_id=s_id)

    order_status_counts = orders_within_category.values('status').annotate(count=Count('status')).order_by()

    # 转换查询结果为字典
    status_counts_dict = dict(order_status_counts.values_list('status', 'count'))

    return status_counts_dict


def shop_profile(request):
    context = {}
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    if role == 'shop':
        shop = get_object_or_404(Shops, s_id=s_id)
        if s_id:
            # 获取该商家所有的唯一订单ID
            unique_order_ids = OrderDetails.objects.filter(shop__s_id=s_id).values_list('order', flat=True).distinct()

            # 根据这些唯一的订单ID统计每个状态的订单数量
            order_status_counts = Orders.objects.filter(o_id__in=unique_order_ids).values('status').annotate(
                count=Count('status'))

            # 统计该商家所有商品的审核状态数量
            product_audit_status_counts = ShopProducts.objects.filter(shop__s_id=s_id).values(
                'product_auditstatus').annotate(count=Count('product_auditstatus'))
            # 转换查询结果为字典
            status_counts = {status_count['status']: status_count['count'] for status_count in order_status_counts}
            audit_status_counts = {status_count['product_auditstatus']: status_count['count'] for status_count in
                                   product_audit_status_counts}
            context = {
                's_name': shop.s_name,
                's_phone': shop.s_phone,
                'email': shop.email,
                'address': shop.address,
                'order_status_counts': status_counts,
                'product_audit_status_counts': audit_status_counts,
                'role': role,
            }
    return render(request, 'shop_profile.html', context)


def edit_shop_profile(request):
    context = {}
    s_id = request.session.get('s_id')
    role = request.session.get('role')
    if role == 'shop':
        shop = get_object_or_404(Shops, s_id=s_id)
        if request.method == 'POST':
            # 处理表单提交
            shop.s_name = request.POST.get('s_name')
            shop.s_psw = request.POST.get('s_psw')
            shop.s_phone = request.POST.get('s_phone')
            shop.email = request.POST.get('email')
            shop.address = request.POST.get('address')
            shop.save()
            # 发送成功消息
            messages.success(request, '资料修改成功！')
            return redirect('edit_shop_profile')
        else:
            # 显示表单
            context = {
                'shop': shop,
                'role': role,
            }
    return render(request, 'edit_shop_profile.html', context)


def myproducts(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    # 从GET请求中获取查询和类别ID
    query = request.GET.get('query', '').strip()
    category_id = request.GET.get('category_id', 0)
    if category_id == 'None':
        category_id = 0
    category_id = int(category_id)
    if query.lower() == 'none' or query == '请输入想找的宝贝':
        query = ''
    # 处理基于查询的商品搜索
    if query is not None and query != '请输入想找的宝贝' and query != '':
        if category_id == 0:
            ids = Products.objects.filter(
                Q(p_name__icontains=query) |
                Q(brand__icontains=query)
            ).values_list('p_id', flat=True)
        else:
            ids = Products.objects.filter(
                (Q(p_name__icontains=query) |
                 Q(brand__icontains=query)) &
                Q(p_type__category_id=category_id)
            ).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(product_id__in=ids, shop__s_id=s_id)
    else:
        if category_id == 0:
            shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
            query = None
        else:
            shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product__p_type__category_id=category_id)
            query = None

    products = Products.objects.all()
    # 计算并设置折扣成百分比形式
    for shop_product in shop_products:
        if hasattr(shop_product, 'discount'):
            shop_product.discount = shop_product.discount * 100

    paginator = Paginator(shop_products, 8)  # 每页显示 8 个商品
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 检查用户是否已经登录
    if 's_id' in request.session:
        template_name = 'shop_my_products.html'
    else:
        template_name = '首页.html'

    context = {'shop_products': page_obj, 'products': products, 'query': query, 'category_id': category_id}
    return render(request, template_name, context)


def shop_productdetails(request, p_id):
    s_id = request.session.get('s_id')

    # 获取商店产品和产品具体信息
    shop_product = ShopProducts.objects.get(shop_product_id=p_id)
    product = Products.objects.get(p_id=shop_product.product.p_id)
    category_id = product.p_type.category_id

    # 定义时间范围：今天和7天前
    today = timezone.now().date()
    date_7_days_ago = timezone.now().date() - timedelta(days=6)

    # 获取相关订单详情信息，并进行汇总求和
    aggregates = OrderDetails.objects.filter(
        product__product_id=p_id,
        shop_id=s_id,
        order__status__in=['待发货', '待收货', '已收货', '已完成']
    ).aggregate(
        total_sales=Sum('quantity'),  # 总销售量
        sales_last_7_days=Sum('quantity', filter=Q(order__o_time__gte=date_7_days_ago)),  # 过去7天销量
        sales_today=Sum('quantity', filter=Q(order__o_time__date=today))  # 当日销量
    )

    total_sales_count = aggregates['total_sales'] or 0
    sales_last_7_days_count = aggregates['sales_last_7_days'] or 0
    sales_today_count = aggregates['sales_today'] or 0

    # 获取7天内的销售数据，按天分组并计算每天的销售总量
    daily_sales_for_last_7_days = OrderDetails.objects.filter(
        product__product_id=p_id,
        shop_id=s_id,
        order__o_time__gte=date_7_days_ago,
        order__status__in=['待发货', '待收货', '已收货', '已完成']
    ).annotate(
        date=TruncDay('order__o_time')  # 按订单时间的天进行分组
    ).values(
        'date'  # 指定我们需要返回的分组字段
    ).annotate(
        daily_sales=Sum('quantity')  # 计算每天的销售总量
    ).order_by('date')  # 按日期

    # 创建一个包含最近七天的日期列表
    seven_days_dates = [(timezone.now().date() - timedelta(days=i)).strftime("%m-%d") for i in range(6, -1, -1)]

    # 将查询集结果转换为字典，日期作为键，每日销售总量作为值，注意日期格式需要与上面的列表一致
    daily_sales_dict = {sales['date'].strftime("%m-%d"): sales['daily_sales'] for sales in
                        daily_sales_for_last_7_days}

    # 根据seven_days_dates创建最终的数据列表，缺失的值填充为0
    daily_sales_list = [[date, daily_sales_dict.get(date, 0)] for date in seven_days_dates]
    # 准备上下文数据
    context = {
        'shop_product': shop_product,
        'product': product,
        's_id': s_id,
        'role': request.session.get('role'),
        'category_id': category_id,
        'query': None,
        'total_sales_count': total_sales_count,
        'sales_last_7_days_count': sales_last_7_days_count,
        'sales_today_count': sales_today_count,
        'daily_sales_list': daily_sales_list,
    }

    # 呈现带有上下文数据的页面
    return render(request, 'shop_product_details.html', context)


def manage_products(request):
    # 从会话中获取用户的ID
    s_id = request.session.get('s_id')
    category_id = request.GET.get('category_id', '0')
    if category_id is not None and category_id != '0' and category_id != '':
        types = ProductCategories.objects.filter(category_id=category_id).values_list('category_id', flat=True)
        ids = Products.objects.filter(p_type__in=types).values_list('p_id', flat=True)
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id, product_id__in=ids)
    else:
        # 如果没有接收到 category_id 参数，就获取这个u_id商家的全部商品
        shop_products = ShopProducts.objects.filter(shop__s_id=s_id)
    paginator = Paginator(shop_products, 6)  # 假设每页显示多少个商品
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
    s_id = request.session.get('s_id', None)
    product_name = request.GET.get('product_name', '')
    category_id = request.GET.get('category_id', '0')
    brand = request.GET.get('brand', '')
    description = request.GET.get('description', '')
    status = request.GET.get('status', '')
    audit_status = request.GET.get('audit_status', '')
    max_stock = request.GET.get('max_stock', None)
    min_stock = request.GET.get('min_stock', None)
    min_original_price = request.GET.get('min_original_price', None)
    max_original_price = request.GET.get('max_original_price', None)
    min_discount = request.GET.get('min_discount', None)
    max_discount = request.GET.get('max_discount', None)
    min_current_price = request.GET.get('min_current_price', None)
    max_current_price = request.GET.get('max_current_price', None)

    queryset = ShopProducts.objects.filter(shop__s_id=s_id) if s_id else ShopProducts.objects.none()

    # 构建查询过滤条件
    query_conditions = Q()
    if product_name:
        query_conditions &= Q(product__p_name__icontains=product_name)
    if category_id != '0':
        query_conditions &= Q(product__p_type__category_id=category_id)
    if brand:
        query_conditions &= Q(product__brand__icontains=brand)
    if description:
        query_conditions &= Q(product_desc__icontains=description)
    if status:
        query_conditions &= Q(product_status__iexact=status)
    if audit_status:
        query_conditions &= Q(product_auditstatus__iexact=audit_status)
    if min_stock:
        query_conditions &= Q(stock_quantity__gte=min_stock)
    if max_stock:
        query_conditions &= Q(stock_quantity__lte=max_stock)
    # 调整为处理价格和折扣的范围搜索
    if min_original_price:
        queryset = queryset.filter(original_price__gte=min_original_price)
    if max_original_price:
        queryset = queryset.filter(original_price__lte=max_original_price)
    if min_discount:
        queryset = queryset.filter(discount__gte=min_discount)
    if max_discount:
        queryset = queryset.filter(discount__lte=max_discount)
    if min_current_price:
        queryset = queryset.filter(current_price__gte=min_current_price)
    if max_current_price:
        queryset = queryset.filter(current_price__lte=max_current_price)

    queryset = queryset.filter(query_conditions)
    # 如果查询集为空，添加一条没有找到商品的消息
    if not queryset.exists():
        messages.info(request, '此搜索条件下没有找到商品！')

    paginator = Paginator(queryset, 6)  # 调整页数到10，或其他适合你应用的数字
    page = request.GET.get('page')
    shop_products = paginator.get_page(page)

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
    # 将搜索字段回传到模板中，以便保持搜索条件
    context = {
        'shop_products': shop_products,
        'product_name': product_name,
        'category_id': category_id,
        'brand': brand,
        'description': description,
        'status': status,
        'audit_status': audit_status,
        'max_stock': max_stock,
        'min_stock': min_stock,
        'min_original_price': min_original_price,
        'max_original_price': max_original_price,
        'min_discount': min_discount,
        'max_discount': max_discount,
        'min_current_price': min_current_price,
        'max_current_price': max_current_price,
        'product_form': product_form,
        'shop_product_form': shop_product_form,
        'message': '此搜索条件下没有找到商品！' if not shop_products else '',
        'query': None
    }

    return render(request, 'shop_manage_products.html', context)


def edit_product(request, product_id):
    # 获取商品对象
    shop_product = get_object_or_404(ShopProducts, pk=product_id)
    product = shop_product.product

    if request.method == "POST":
        # 使用POST和FILES数据以及现有实例初始化表单
        product_form = ProductForm(request.POST, request.FILES, instance=product)
        shop_product_form = ShopProductForm(request.POST, request.FILES, instance=shop_product)

        # 验证表单
        if product_form.is_valid() and shop_product_form.is_valid():
            # 确定哪些字段发生了变化
            form_changes = product_form.changed_data or shop_product_form.changed_data
            # 获取状态变化情况
            status_changed = 'product_status' in shop_product_form.changed_data
            # 获取当前审核状态
            audit_approved = shop_product.product_auditstatus == '审核通过'
            # 获取商品状态变化值
            new_status = shop_product_form.cleaned_data.get('product_status')

            # 审核通过的商品仅当状态发生变化时才处理
            if audit_approved and status_changed and len(form_changes) == 1:
                # 如果是审核通过且只有状态变化，更新状态不改变审核状态
                product_form.save()
                shop_product_form.save()
                messages.success(request, '商品信息已更新')
            else:
                # 否则考虑表单的其他变化，需要设置为待审核
                shop_product = shop_product_form.save(commit=False)
                shop_product.product_auditstatus = '待审核'
                shop_product.product_status = '下架' if new_status != '上架' else new_status

                # 处理商品图片变化
                if 'product_image' in request.FILES:
                    fs = FileSystemStorage(location='static/商品图片')
                    if shop_product.product_image_url:
                        fs.delete(shop_product.product_image_url)
                    myfile = request.FILES['product_image']
                    filename = fs.save(myfile.name, myfile)
                    shop_product.product_image_url = fs.url(filename)

                # 保存变更
                product_form.save()
                shop_product.save()
                messages.success(request, '商品信息已更新，待审核状态。')
            return redirect('edit_product', product_id=product_id)
        else:
            # 如果表单验证未通过，显示错误消息
            messages.error(request, '表单信息填写有误，请检查后重新提交。')

    else:
        # 对于GET请求，用现有实例初始化表单
        product_form = ProductForm(instance=product)
        shop_product_form = ShopProductForm(instance=shop_product)

    # 获取类别ID
    category_id = product.p_type.category_id
    context = {
        'product_form': product_form,
        'shop_product_form': shop_product_form,
        'shop_products': shop_product,
        'products': product,
        'category_id': category_id,
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
    shop_product = get_object_or_404(ShopProducts, shop_product_id=product_id)

    # 检查商品是否正在上架
    if shop_product.product_status == ShopProducts.ProductStatus.ON_SALE:
        messages.error(request, "删除失败！商品还在上架中！")
        return redirect('manage_products')

    # 检查商品最近7天内是否有未完成的订单
    recent_orders = OrderDetails.objects.filter(
        product=shop_product,
        order__o_time__gte=timezone.now() - timedelta(days=7)
    ).exclude(
        order__status__in=['已完成', '已取消', '已退货']
    ).exists()

    # 如果有未完成的订单，返回消息
    if recent_orders:
        messages.warning(request, "删除失败！商品还有订单未完成！")
        return redirect('manage_products')

    # 如果商品有图片，尝试删除图片
    if shop_product.product_image_url:
        image_path = shop_product.product_image_url
        fs = FileSystemStorage(location='static/商品图片')  # 创建一个文件系统存储对象
        fs.delete(shop_product.product_image_url)  # 删除图片文件
        if fs.exists(shop_product.product_image_url):  # 检查文件是否仍然存在
            print("删除图片错误")  # 如果文件仍然存在，打印一条错误消息
        pass

    # 安全删除商品记录
    shop_product.delete()
    messages.success(request, "商品已成功删除。")
    return redirect('manage_products')  # 重定向到manage_products视图


def shop_order(request):
    # 从会话中获取当前登录的商家ID
    shop_id = request.session.get('s_id')

    # 查询这个商家的所有订单
    order_ids = OrderDetails.objects.filter(shop__s_id=shop_id).values_list('order__o_id', flat=True)
    orders = Orders.objects.filter(o_id__in=order_ids)
    # 分页
    paginator = Paginator(orders, 10)  # 例如每页显示10条记录
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    # 将订单传递给模板
    context = {
        'orders': paged_orders,
        'category_id': '0',  # 用于保持搜索条件
        'query': None
    }
    return render(request, 'shop_order.html', context)


def shop_search_orders(request):
    # 为所有可能的搜索字段获取值
    s_id = request.session.get('s_id', None)
    product_name = request.GET.get('product_name', '')
    category_id = request.GET.get('category_id', '0')
    brand = request.GET.get('brand', '')
    description = request.GET.get('description', '')
    status = request.GET.get('status', '')
    audit_status = request.GET.get('audit_status', '')
    max_stock = request.GET.get('max_stock', None)
    min_stock = request.GET.get('min_stock', None)
    min_original_price = request.GET.get('min_original_price', None)
    max_original_price = request.GET.get('max_original_price', None)
    min_discount = request.GET.get('min_discount', None)
    max_discount = request.GET.get('max_discount', None)
    min_current_price = request.GET.get('min_current_price', None)
    max_current_price = request.GET.get('max_current_price', None)

    order_status = request.GET.get('order_status', '')
    min_order_total_price = request.GET.get('min_order_total_price', None)
    max_order_total_price = request.GET.get('max_order_total_price', None)
    min_paid_time = request.GET.get('min_paid_time', None)
    max_paid_time = request.GET.get('max_paid_time', None)
    order_address = request.GET.get('order_address', '')
    min_created_time = request.GET.get('min_created_time', None)
    max_created_time = request.GET.get('max_created_time', None)

    user_name = request.GET.get('user_name', '')
    user_phone = request.GET.get('user_phone', '')
    user_sex = request.GET.get('user_sex', '')
    user_email = request.GET.get('user_email', '')
    # 构建查询条件
    query_conditions = Q()
    # 只展示当前商家(s_id)的订单
    if s_id:
        query_conditions &= Q(orderdetails__shop__s_id=s_id)
        # 'status' 是定义在 Orders 模型中的状态字段
        order_status_counts = Orders.objects.filter(orderdetails__shop__s_id=s_id).values('status').annotate(
            count=Count('status'))
    else:
        order_status_counts = Orders.objects.none()
    if product_name:
        query_conditions &= Q(orderdetails__product__product__p_name__icontains=product_name)
    if category_id != '0':
        query_conditions &= Q(orderdetails__product__product__p_type_id=category_id)
    if brand:
        query_conditions &= Q(orderdetails__product__product__brand__icontains=brand)
    # 注意这里如果其他商家的product名称和商家的product描述相同，这一filter也能提取出其他商家的商品
    if description:
        query_conditions &= Q(orderdetails__product__product_desc__icontains=description)
    if status:  # 注意，这里的字段可能指的是ShopProducts的上架状态
        query_conditions &= Q(orderdetails__product__product_status=status)
    if audit_status:  # 注意，这里可能指的是ShopProducts的审核状态
        query_conditions &= Q(orderdetails__product__product_auditstatus=audit_status)
    if min_stock:
        query_conditions &= Q(orderdetails__product__stock_quantity__gte=min_stock)
    if max_stock:
        query_conditions &= Q(orderdetails__product__stock_quantity__lte=max_stock)
    if min_original_price:
        query_conditions &= Q(orderdetails__product__original_price__gte=min_original_price)
    if max_original_price:
        query_conditions &= Q(orderdetails__product__original_price__lte=max_original_price)
    if min_discount:
        query_conditions &= Q(orderdetails__product__discount__gte=min_discount)
    if max_discount:
        query_conditions &= Q(orderdetails__product__discount__lte=max_discount)
    if min_current_price:
        query_conditions &= Q(orderdetails__product__current_price__gte=min_current_price)
    if max_current_price:
        query_conditions &= Q(orderdetails__product__current_price__lte=max_current_price)
    if order_status:
        query_conditions &= Q(status=order_status)
    if min_order_total_price:
        query_conditions &= Q(total_price__gte=min_order_total_price)
    if max_order_total_price:
        query_conditions &= Q(total_price__lte=max_order_total_price)
    if order_address:
        query_conditions &= Q(order_address__icontains=order_address)
        # 统一处理时间字符串
    if min_paid_time and min_paid_time != 'None':
        min_paid_time = datetime.strptime(min_paid_time, '%Y-%m-%d').date()
    else:
        min_paid_time = None

    if max_paid_time and max_paid_time != 'None':
        max_paid_time = datetime.strptime(max_paid_time, '%Y-%m-%d').date()
    else:
        max_paid_time = None

    # 对提供的创建时间字符串进行处理
    if min_created_time and min_created_time != 'None':
        min_created_time = datetime.strptime(min_created_time, '%Y-%m-%d').date()
    else:
        min_created_time = None

    if max_created_time and max_created_time != 'None':
        max_created_time = datetime.strptime(max_created_time, '%Y-%m-%d').date()
    else:
        max_created_time = None

    # 如果最小和最大时间相同，表示搜索特定一天的订单
    if min_paid_time and max_paid_time and min_paid_time == max_paid_time:
        start_of_day = datetime.combine(min_paid_time, datetime.min.time())
        end_of_day = datetime.combine(min_paid_time, datetime.max.time())
        query_conditions &= Q(paid_time__range=(start_of_day, end_of_day))
    else:
        if min_paid_time:
            start_of_day = datetime.combine(min_paid_time, datetime.min.time())
            query_conditions &= Q(paid_time__gte=start_of_day)
        if max_paid_time:
            end_of_day = datetime.combine(max_paid_time, datetime.max.time())
            query_conditions &= Q(paid_time__lte=end_of_day)

    # 如果最小和最大创建时间相同，表示搜索特定一天的订单
    if min_created_time and max_created_time and min_created_time == max_created_time:
        start_of_day = datetime.combine(min_created_time, datetime.min.time())
        end_of_day = datetime.combine(max_created_time, datetime.max.time())
        query_conditions &= Q(o_time__range=(start_of_day, end_of_day))
    else:
        # 如果最小创建时间被指定，搜索从那一天开始的订单
        if min_created_time:
            start_of_day = datetime.combine(min_created_time, datetime.min.time())
            query_conditions &= Q(o_time__gte=start_of_day)
        # 如果最大创建时间被指定，搜索直到那一天结束的订单
        if max_created_time:
            end_of_day = datetime.combine(max_created_time, datetime.max.time())
            query_conditions &= Q(o_time__lte=end_of_day)
    if user_name:
        query_conditions &= Q(user__u_name__icontains=user_name)
    if user_phone:
        query_conditions &= Q(user__u_phone__icontains=user_phone)
    if user_sex:
        query_conditions &= Q(user__u_sex=user_sex)
    if user_email:
        query_conditions &= Q(user__email__icontains=user_email)
    # 应用查询条件
    orders = Orders.objects.filter(query_conditions).distinct() if query_conditions else Orders.objects.none()

    # 分页
    paginator = Paginator(orders, 10)  # 例如每页显示10条记录
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)
    # 创建一个字典来存储每种状态的订单数量
    status_counts = {status_count['status']: status_count['count'] for status_count in order_status_counts}

    # 将搜索字段回传到模板中，以便保持搜索条件
    context = {
        'orders': paged_orders,
        'product_name': product_name,
        'category_id': category_id,
        'brand': brand,
        'description': description,
        'status': status,
        'audit_status': audit_status,
        'max_stock': max_stock,
        'min_stock': min_stock,
        'min_original_price': min_original_price,
        'max_original_price': max_original_price,
        'min_discount': min_discount,
        'max_discount': max_discount,
        'min_current_price': min_current_price,
        'max_current_price': max_current_price,
        'order_status': order_status,
        'min_order_total_price': min_order_total_price,
        'max_order_total_price': max_order_total_price,
        'order_address': order_address,
        'min_paid_time': min_paid_time.strftime('%Y-%m-%d') if min_paid_time else None,
        'max_paid_time': max_paid_time.strftime('%Y-%m-%d') if max_paid_time else None,
        'min_created_time': min_created_time.strftime('%Y-%m-%d') if min_created_time else None,
        'max_created_time': max_created_time.strftime('%Y-%m-%d') if max_created_time else None,
        'user_name': user_name,
        'user_phone': user_phone,
        'user_email': user_email,
        'user_sex': user_sex,
        'order_status_counts': status_counts,
        'query': None
    }

    return render(request, 'shop_order.html', context)


def user_detail(request, user_id):
    user = get_object_or_404(Users, pk=user_id)
    data = {
        'u_name': user.u_name,
        'u_sex': user.u_sex,
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


def return_product(request, o_id):
    if request.method == 'POST':
        try:
            # 在数据库中查找订单实例
            order = Orders.objects.get(o_id=o_id)
            # 检查订单状态是否为"待发货"
            if order.status == '待退货':
                # 修改订单状态为"待收货"
                order.status = '已退货'
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


def get_time_range(request):
    # 初始化months变量
    months = None

    if request.method == 'POST':
        # 从POST请求中获取months的值
        months = request.POST.get('months')

        # 现在，months变量包含了<select>的值，你可以根据这个值进行后续处理
        # 比如，重定向到另一个视图或者渲染一个新页面
        return redirect('some_other_view')

    # 如果是GET请求，就渲染表单
    return render(request, 'rfm.html')


def rfm_analysis(request):
    engine = create_engine('mysql+pymysql://web:dzh20030112@47.93.125.169/web')
    products_data = pd.read_sql_query('select * from products', engine)
    orders_data = pd.read_sql_query("select * from orders", engine)
    order_details_data = pd.read_sql_query("select * from order_details", engine)
    user_data = pd.read_sql_query("select u_name,u_id from users", engine)

    # 转换时间类型
    orders_data['o_time'] = pd.to_datetime(orders_data['o_time'])
    orders_data['paid_time'] = pd.to_datetime(orders_data['paid_time'])
    # 将表融合
    merged_data = pd.merge(orders_data, order_details_data, left_on='o_id', right_on='order_id')
    merged_data = pd.merge(merged_data, products_data, left_on='product_id', right_on='p_id')
    merged_data = pd.merge(merged_data, user_data, left_on='user_id', right_on='u_id')

    # 筛选出两年之内的购买记录
    current_time = pd.Timestamp.now()
    time_range = current_time - relativedelta(years=2)
    filtered_data = merged_data[(merged_data['paid_time'] >= time_range) &
                                (merged_data['paid_time'] <= current_time)]

    # 根据当下的商铺号来筛选订单
    shop_id = request.session.get('s_id')
    filtered_data = filtered_data.query(f'shop_id == {shop_id}')

    # 创建一个空的DataFrame来存储RFM值
    RFM = pd.DataFrame()
    # 计算R（最近一次购买时间）注意，这个R是dataframe格式
    R = filtered_data.groupby('u_id')['paid_time'].max().reset_index()
    R.columns = ['u_id', 'last_purchase_time']  # 重命名列以避免混淆
    RFM['u_id'] = R['u_id']
    RFM['Recency'] = (pd.Timestamp.now() - R['last_purchase_time']).dt.days
    # 计算F（购买频次）
    F = filtered_data.groupby('u_id').size().reset_index(name='frequency')
    # 使用size()来计算每个组的行数,即该u_id在这一段时间内共出现了多少次。
    RFM['Frequency'] = F['frequency']
    # 计算M（总消费金额）
    M = filtered_data.groupby('u_id')['total_price'].sum().reset_index()
    RFM['Monetary'] = M['total_price']
    # 平均值作为阈值
    R_threshold = RFM['Recency'].mean()
    F_threshold = RFM['Frequency'].mean()
    M_threshold = RFM['Monetary'].mean()

    # 标识高于(1)或低于(0)平均值
    RFM['R'] = (RFM['Recency'] <= R_threshold).astype(int)
    RFM['F'] = (RFM['Frequency'] >= F_threshold).astype(int)
    RFM['M'] = (RFM['Monetary'] >= M_threshold).astype(int)

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

    # 获取选择的RFM标签
    selected_rfm_label = request.GET.get('category_id')

    # 如果有选择的RFM标签，则筛选数据
    if selected_rfm_label and selected_rfm_label != 'all':
        RFM_data = [d for d in RFM_data if d['RFM_Label'] == selected_rfm_label]
    # 创建一个字典，其中包含您想要在模板中使用的数据
    # 分页
    paginator = Paginator(RFM_data, 10)  # 例如每页显示10条记录
    page = request.GET.get('page')
    paged_data = paginator.get_page(page)

    context = {
        'RFM_data': paged_data,
        'category_id': '0',  # 用于保持搜索条件
        'selected_rfm_label': selected_rfm_label or 'all',
        'time_range': time_range,
        'query': None
        # 如果您还有其他数据需要传递，可以在这里添加
    }

    # 渲染模板，并将上下文传递给模板
    return render(request, 'rfm.html', context)
