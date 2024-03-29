from django.urls import path
from . import views

urlpatterns = [
    path('shoppage/', views.shoppage, name='shoppage'),
    path('shoppage/get_products_fromshop/', views.get_products_fromshop, name='get_products_fromshop'),
    path('shoppage/myproducts/', views.myproducts, name='myproducts'),
    path('shoppage/manage_products/', views.manage_products, name='manage_products'),
    path('shoppage/shop_order/', views.shop_order, name='shop_order'),
    path('shoppage/sales_analysis/', views.sales_analysis, name='sales_analysis'),
]