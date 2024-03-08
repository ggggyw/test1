from django.db import models

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

class Admin(models.Model):
    ad_id = models.AutoField(primary_key=True)
    ad_acc = models.CharField(max_length=10)
    ad_psw = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = 'admin'


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