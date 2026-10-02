from django.db import models


class Product(models.Model):
    name = models.CharField("نام", max_length=200)
    category = models.CharField("دسته‌بندی", max_length=100, db_index=True)
    price = models.PositiveIntegerField("قیمت (تومان)")
    image_url = models.URLField("آدرس تصویر", blank=True)
    stock = models.PositiveIntegerField("موجودی", default=0)
    is_active = models.BooleanField("فعال", default=True)

    def __str__(self):
        return self.name


class DiscountCode(models.Model):
    code = models.CharField("کد", max_length=30, unique=True)
    percent = models.PositiveSmallIntegerField("درصد تخفیف")
    is_active = models.BooleanField("فعال", default=True)

    def __str__(self):
        return f"{self.code} ({self.percent}%)"


class Order(models.Model):
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=11)
    address = models.TextField()
    discount_code = models.ForeignKey(DiscountCode, null=True, blank=True, on_delete=models.SET_NULL)
    subtotal = models.PositiveIntegerField()
    discount = models.PositiveIntegerField()
    shipping = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"سفارش #{self.pk}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.PositiveIntegerField()  # price at order time
