from django.urls import path
from stu import views as stu_views

urlpatterns=[
    path('user/login/', stu_views.login, name='login'),
    path('user/register/', stu_views.register, name='register'),
    path('', stu_views.home, name='home'),
]