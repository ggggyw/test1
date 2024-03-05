from django.urls import path
from login_register import views as login_register_views

urlpatterns=[
    path('user/login/', login_register_views.login, name='login'),
    path('user/register/', login_register_views.register, name='register'),
    path('', login_register_views.home, name='home'),
]