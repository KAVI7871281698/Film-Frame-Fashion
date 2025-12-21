from django.contrib import admin
from .models import product,Order,home,Coupon
# Register your models here.

admin.site.register(product)
admin.site.register(Order)
admin.site.register(home)
admin.site.register(Coupon)