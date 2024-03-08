from django.db import models

class User(models.Model):
    u_id = models.AutoField(primary_key=True)
    u_acc = models.CharField(unique=True, max_length=10)
    u_psw = models.CharField(max_length=20)
    u_name = models.CharField(max_length=20)
    u_sex = models.CharField(max_length=1)
    u_phone = models.CharField(max_length=11)

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