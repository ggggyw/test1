"""
URL configuration for djangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from djangoProject import views
from djangoProject.views import logout_view
from user import views as user_views
from django.conf import settings
from django.conf.urls.static import static
from login_register import views as login_register_views
from user.views import follow_shop, unfollow_shop


urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', logout_view, name='logout'),
    path('user/register/', login_register_views.register, name='register'),
    path('user/login/', login_register_views.login, name='login'),
    path('userpage/', user_views.userpage, name='userpage'),
    path('user/userprofile/', user_views.userprofile, name='userprofile'),
    path('user/usercart',user_views.usercart, name='usercart'),
    path('user/userpage/productdetails/<int:p_id>/', user_views.product_details, name='product_details'),
    path('', views.home, name='home'),
    path('user/userorder',user_views.userorder, name='userorder'),
    path('user/userserve',user_views.userserve, name='userserve'),
    path('delete_item/',user_views.delete_item, name='delete_item'),
    path('checkout/',user_views.checkout, name='delete_item'),
    path('update_quantity/',user_views.update_quantity, name='update_quantity'),
    path('add-to-cart/',user_views.add_to_cart, name='add_to_cart'),
    path('home/', views.home, name='home'),
    path('get_products/', views.get_products, name='get_products'),
    path('shop/', include('shop.urls')),
    path('user_orders/', user_views.user_orders, name='user_orders'),
    path('follow-shop/<int:shop_id>/', follow_shop, name='follow_shop'),
    path('unfollow-shop/<int:shop_id>/', unfollow_shop, name='unfollow_shop'),
    path('search/', views.search_products, name='search_products'),
    path('user/userprofile/edit_userprofile/', user_views.edit_userprofile, name='edit_userprofile'),
    path('user/address/', user_views.user_addresses, name='user_addresses'),
    path('api/default-address/', user_views.get_default_address, name='get_default_address'),
    path('api/other-addresses/', user_views.get_other_addresses, name='get_other_addresses'),
    path('api/add-address/', user_views.add_address, name='add_address'),
    path('api/get-address/<int:address_id>/', user_views.get_address, name='get_address'),
    path('api/edit-address/', user_views.edit_address, name='edit_address'),
    path('api/save-addresses/', user_views.save_addresses, name='save_addresses'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
