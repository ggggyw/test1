from django.urls import path
from stu import views

urlpatterns=[
    path('',views.login)
]