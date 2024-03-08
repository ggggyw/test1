from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, u_acc, u_name, u_psw, u_sex, u_phone, email=None, address=None):
        if not u_acc:
            raise ValueError('Users must have an account')

        user = self.model(
            u_acc=u_acc,
            u_name=u_name,
            u_sex=u_sex,
            u_phone=u_phone,
            email=self.normalize_email(email),
            address=address
        )

        user.set_password(u_psw)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    u_id = models.AutoField(primary_key=True)
    u_acc = models.CharField(max_length=20, unique=True)
    u_name = models.CharField(max_length=20)
    u_psw = models.CharField(max_length=20)
    u_sex = models.CharField(max_length=6, choices=[('male', 'Male'), ('female', 'Female')])
    u_phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=50, unique=True, null=True)
    address = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'u_acc'
    REQUIRED_FIELDS = ['u_name', 'u_sex', 'u_phone']

    def __str__(self):
        return self.u_acc


class AdminManager(BaseUserManager):
    def create_admin(self, ad_acc, ad_psw):
        if not ad_acc:
            raise ValueError('Admin must have an account')

        admin = self.model(
            ad_acc=ad_acc,
        )

        admin.set_password(ad_psw)
        admin.save(using=self._db)
        return admin


class Admin(AbstractBaseUser):
    ad_id = models.AutoField(primary_key=True)
    ad_acc = models.CharField(max_length=20, unique=True)
    ad_psw = models.CharField(max_length=20)

    objects = AdminManager()

    USERNAME_FIELD = 'ad_acc'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.ad_acc


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