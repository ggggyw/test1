from django.db import models

class Users(models.Model):
    u_id = models.IntegerField(primary_key=True)
    u_acc = models.CharField(unique=True, max_length=20)
    u_name = models.CharField(max_length=20)
    u_psw = models.CharField(max_length=20)
    u_sex = models.CharField(max_length=6)
    u_phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=50, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'users'

class Admin(models.Model):
    ad_id = models.IntegerField(primary_key=True)
    ad_acc = models.CharField(unique=True, max_length=20)
    ad_psw = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'admin'


class Shops(models.Model):
    s_id = models.IntegerField(primary_key=True)
    s_name = models.CharField(max_length=20)
    s_acc = models.CharField(unique=True, max_length=20)
    s_psw = models.CharField(max_length=20)
    s_phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=50, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shops'

class ProductCategories(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'product_categories'

class Products(models.Model):
    p_id = models.IntegerField(primary_key=True)
    p_name = models.CharField(max_length=20)
    p_type = models.ForeignKey(ProductCategories, models.DO_NOTHING, db_column='p_type')
    brand = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'


class ShopProducts(models.Model):
    shop_product_id = models.IntegerField(primary_key=True)
    shop = models.ForeignKey('Shops', models.DO_NOTHING)
    product = models.ForeignKey(Products, models.DO_NOTHING)
    product_desc = models.TextField()
    product_status = models.CharField(max_length=2)
    product_image_url = models.CharField(max_length=255, blank=True, null=True)
    stock_quantity = models.IntegerField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shop_products'
