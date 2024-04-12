from django.urls import path
from . import views

urlpatterns = [
    path('shoppage/', views.shoppage, name='shoppage'),
    path('shoppage/myproducts/', views.myproducts, name='myproducts'),
    path('shoppage/manage_products/', views.manage_products, name='manage_products'),
    path('shoppage/manage_products/edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('shoppage/manage_products/add_product/', views.add_product, name='add_product'),
    path('shoppage/manage_products/delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('shoppage/shop_order/', views.shop_order, name='shop_order'),
    path('shoppage/shop_order/user/<int:user_id>/', views.user_detail, name='user-detail-api'),
    path('shoppage/shop_order/product/<int:p_id>/', views.product_detail, name='product-detail-api'),
    path('shoppage/rfm/', views.rfm_analysis, name='rfm_analysis'),
    path('shoppage/shop_productdetails/<int:p_id>/', views.shop_productdetails, name='shop_productdetails'),
]
