from django.db import models
from django.core.validators import RegexValidator

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
    

class add_to_cart(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    add_to_cart_product = models.ForeignKey(product, on_delete=models.CASCADE)
    
    quantity = models.PositiveIntegerField(default=1)

    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.add_to_cart_product.product_price

    def __str__(self):
        return f"{self.add_to_cart_product.product_name} - {self.quantity}"
    

class Order(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.TextField(null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
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


    
    