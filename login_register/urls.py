from django.urls import path
from login_register import views as login_register_views
from djangoProject import views
from user import views as user_views

urlpatterns=[
    path('user/login/', login_register_views.login, name='login'),
    path('user/register/', login_register_views.register, name='register'),
    path('user/userpage/', user_views.userpage, name='userspage'),
    path('', views.home, name='home'),
]
