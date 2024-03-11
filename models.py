# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    ad_id = models.IntegerField(primary_key=True)
    ad_acc = models.CharField(unique=True, max_length=20)
    ad_psw = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'admin'


class Carts(models.Model):
    product = models.ForeignKey('ShopProducts', models.DO_NOTHING)
    user = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True)  # The composite primary key (user_id, product_id, shop_id) found, that is not supported. The first column is selected.
    shop = models.ForeignKey('Shops', models.DO_NOTHING)
    join_time = models.DateTimeField()
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'carts'
        unique_together = (('user', 'product', 'shop'),)


class Comments(models.Model):
    c_id = models.IntegerField(primary_key=True)
    p = models.ForeignKey('ShopProducts', models.DO_NOTHING)
    s = models.ForeignKey('Shops', models.DO_NOTHING)
    u = models.ForeignKey('Users', models.DO_NOTHING)
    flag = models.CharField(max_length=2)
    content = models.TextField()
    c_time = models.DateTimeField()
    reply_to = models.ForeignKey('self', models.DO_NOTHING, db_column='reply_to', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'comments'


class Followers(models.Model):
    u = models.OneToOneField('Users', models.DO_NOTHING, primary_key=True)  # The composite primary key (u_id, s_id) found, that is not supported. The first column is selected.
    s = models.ForeignKey('Shops', models.DO_NOTHING)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'followers'
        unique_together = (('u', 's'),)


class OrderDetails(models.Model):
    order_detail_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    product = models.ForeignKey('ShopProducts', models.DO_NOTHING)
    shop = models.ForeignKey('Shops', models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_details'


class Orders(models.Model):
    o_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    status = models.CharField(max_length=3)
    paid_time = models.DateTimeField(blank=True, null=True)
    o_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'orders'


class ProductCategories(models.Model):
    category_id = models.IntegerField(primary_key=True)
    category_name = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'product_categories'


class Products(models.Model):
    p_id = models.IntegerField(primary_key=True)
    p_name = models.CharField(max_length=20)
    p_type = models.ForeignKey(ProductCategories, models.DO_NOTHING, db_column='p_type')
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

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


class Shops(models.Model):
    s_id = models.IntegerField(primary_key=True)
    s_name = models.CharField(max_length=20)
    s_acc = models.CharField(unique=True, max_length=20)
    s_psw = models.CharField(max_length=20)
    s_phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=50, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'shops'


class UserAddresses(models.Model):
    address_id = models.IntegerField(primary_key=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    address = models.CharField(max_length=100)
    is_default = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_addresses'


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
        managed = False
        db_table = 'users'
