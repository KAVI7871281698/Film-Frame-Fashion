from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be exactly 10 digits."
)

class Register(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone = models.CharField(
        max_length=10,
        validators=[phone_validator],
        unique=True
    )
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)

class product(models.Model):
    product_img = models.ImageField(upload_to='uploads', null=True,blank=True)
    product_Categorie = models.CharField(max_length=50,null=True)
    product_name = models.CharField(max_length=100)
    product_des = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    
class home(models.Model):
    bannerimg1 = models.ImageField(upload_to='uploads', null=True,blank=True)
    bannerimg2 = models.ImageField(upload_to='uploads', null=True,blank=True)
    bannervideo = models.FileField(upload_to='uploads/banners/videos/',null=True,blank=True)


class add_to_cart(models.Model):
    user = models.ForeignKey(
        Register,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )

    add_to_cart_product = models.ForeignKey(
        product,
        on_delete=models.CASCADE,
        related_name='cart_products'
    )

    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'add_to_cart_product')
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"

    @property
    def total_price(self):
        return self.quantity * self.add_to_cart_product.product_price

    def __str__(self):
        return f"{self.user.email} | {self.add_to_cart_product.product_name} x {self.quantity}"

    

class Order(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    delivery_address = models.TextField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)

    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Failed', 'Failed'),
        ],
        default='Pending'
    )

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Confirmed', 'Confirmed'),
            ('Delivered', 'Delivered'),
            ('Cancelled', 'Cancelled'),
        ],
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.email}"
    

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)

    DISCOUNT_TYPE = (
        ('flat', 'Flat Amount'),
        ('percent', 'Percentage'),
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE)
    discount_value = models.PositiveIntegerField()

    min_order_amount = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)
    expiry_date = models.DateField()

    max_uses = models.PositiveIntegerField(default=10)
    used_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return (
            self.is_active and
            self.used_count < self.max_uses and
            self.expiry_date >= timezone.now().date()
        )

    def __str__(self):
        return self.code


    
    