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
from user import views as user_views
from django.conf import settings
from django.conf.urls.static import static

from login_register import views as login_register_views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/register/', login_register_views.register, name='register'),
    path('user/login/', login_register_views.login, name='login'),
    path('userpage/<int:ID>/<str:role>/', user_views.userpage, name='userpage'),
    path('user/userprofile/<int:ID>/<str:role>/', user_views.userprofile, name='userprofile'),
    path('user/usercart',user_views.usercart, name='usercart'),
    path('user/userpage/productdetails/<int:p_id>/', user_views.product_details, name='product_details'),
    path('', views.home, name='home'),
    path('user/userorder',user_views.userorder, name='userorder'),
    path('user/userserve',user_views.userserve, name='userserve'),
    path('add-to-cart/',user_views.add_to_cart, name='add_to_cart'),#没想好要不要删掉
    path('home/', views.home, name='home'),
    path('get_products/', views.get_products, name='get_products'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
