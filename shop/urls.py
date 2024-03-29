from django.urls import path
from . import views

urlpatterns = [
    path('shoppage/', views.shoppage, name='shoppage'),
    path('shoppage/get_products_fromshop/', views.get_products_fromshop, name='get_products_fromshop'),
]