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
    description = models.TextField(blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'products'