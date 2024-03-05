# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Admin(models.Model):
    ad_id = models.AutoField(primary_key=True)
    ad_acc = models.CharField(max_length=10)
    ad_psw = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'admin'


class Cart(models.Model):
    p = models.ForeignKey('Product', models.DO_NOTHING)
    u = models.ForeignKey('User', models.DO_NOTHING)
    join_time = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cart'


class Comments(models.Model):
    comment = models.TextField()

    class Meta:
        managed = True
        db_table = 'comments'


class Concern(models.Model):
    u = models.ForeignKey('User', models.DO_NOTHING)
    m = models.ForeignKey('Merchant', models.DO_NOTHING)

    class Meta:
        managed = True
        db_table = 'concern'


class Forum(models.Model):
    f_id = models.AutoField(primary_key=True)
    u = models.ForeignKey('User', models.DO_NOTHING, blank=True, null=True)
    m = models.ForeignKey('Merchant', models.DO_NOTHING, blank=True, null=True)
    f_time = models.DateTimeField(blank=True, null=True)
    f_con = models.CharField(max_length=200)
    reply_to = models.IntegerField(blank=True, null=True)
    flag = models.CharField(max_length=2)

    class Meta:
        managed = True
        db_table = 'forum'


class Merchant(models.Model):
    m_id = models.AutoField(primary_key=True)
    m_acc = models.CharField(unique=True, max_length=10)
    m_psw = models.CharField(max_length=20)
    m_name = models.CharField(max_length=20)
    m_sex = models.CharField(max_length=1)
    m_tele = models.CharField(max_length=11)

    class Meta:
        managed = True
        db_table = 'merchant'


class Orders(models.Model):
    p = models.ForeignKey('Product', models.DO_NOTHING)
    u = models.ForeignKey('User', models.DO_NOTHING)
    buy_time = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField()
    totalprice = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    o_status = models.CharField(max_length=5, blank=True, null=True)
    o_id = models.AutoField(primary_key=True)
    send_time = models.DateTimeField(blank=True, null=True)
    receive_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'orders'


class Product(models.Model):
    p_id = models.AutoField(primary_key=True)
    m = models.ForeignKey(Merchant, models.DO_NOTHING)
    p_name = models.CharField(max_length=20)
    p_desc = models.CharField(max_length=50)
    p_class = models.CharField(max_length=10)
    p_price = models.DecimalField(max_digits=10, decimal_places=2)
    p_status = models.CharField(max_length=3)
    p_img = models.CharField(max_length=50, db_collation='utf8_general_ci', blank=True, null=True)
    p_quantity = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'product'


class ReturnDetail(models.Model):
    r_id = models.AutoField(primary_key=True)
    o = models.ForeignKey(Orders, models.DO_NOTHING)
    request_time = models.DateTimeField(blank=True, null=True)
    reason = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'return_detail'


class User(models.Model):
    u_id = models.AutoField(primary_key=True)
    u_acc = models.CharField(unique=True, max_length=10)
    u_psw = models.CharField(max_length=20)
    u_name = models.CharField(max_length=20)
    u_sex = models.CharField(max_length=1)
    u_tele = models.CharField(max_length=11)

    class Meta:
        managed = True
        db_table = 'user'
