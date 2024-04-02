from django.db import models


class ProductCategories(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=50)

    class Meta:
        db_table = 'product_categories'
    def __str__(self):
        return self.category_name


class Products(models.Model):
    p_id = models.AutoField(primary_key=True)
    p_name = models.CharField(max_length=20)
    p_type = models.ForeignKey(ProductCategories, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'products'


class Shops(models.Model):
    s_id = models.AutoField(primary_key=True)
    s_name = models.CharField(max_length=20)
    s_acc = models.CharField(unique=True, max_length=20)
    s_psw = models.CharField(max_length=20)
    s_phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=50, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'shops'


class ShopProducts(models.Model):
    shop_product_id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    product_desc = models.TextField()
    product_status = models.CharField(max_length=2)
    product_image_url = models.CharField(max_length=255, blank=True, null=True)
    stock_quantity = models.IntegerField()
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'shop_products'


class Users(models.Model):
    u_id = models.AutoField(primary_key=True)
    u_acc = models.CharField(unique=True, max_length=20)
    u_name = models.CharField(max_length=20)
    u_psw = models.CharField(max_length=20)
    u_sex = models.CharField(max_length=6)
    u_phone = models.CharField(max_length=20)
    email = models.CharField(unique=True, max_length=50, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'users'


class Carts(models.Model):
    product = models.ForeignKey(ShopProducts,  on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shops,  on_delete=models.CASCADE)
    join_time = models.DateTimeField()
    quantity = models.IntegerField()

    class Meta:
        db_table = 'carts'
        unique_together = (('user', 'product', 'shop'),)


class Orders(models.Model):
    o_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    status = models.CharField(max_length=3)
    paid_time = models.DateTimeField(blank=True, null=True)
    o_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'orders'


class OrderDetails(models.Model):
    order_detail_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    product = models.ForeignKey(ShopProducts, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shops, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    current_single_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_details'


class Admin(models.Model):
    ad_id = models.AutoField(primary_key=True)
    ad_acc = models.CharField(unique=True, max_length=20)
    ad_psw = models.CharField(max_length=20)
    is_super = models.BooleanField(default=False)

    class Meta:
        db_table = 'admin'


class Followers(models.Model):
    u = models.ForeignKey(Users, on_delete=models.CASCADE)
    s = models.ForeignKey(Shops, on_delete=models.CASCADE)
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'followers'
        unique_together = (('u', 's'),)


class UserAddresses(models.Model):
    address_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    address = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'user_addresses'


