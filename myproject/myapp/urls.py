from django.urls import path,include
from .import views

urlpatterns = [
    path('', views.index, name='index'),

    path('categories', views.categories, name='categories'),
    path('collection', views.collection, name='collection'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),

    path('login', views.login, name='login'),
    path('register', views.register, name='register'),

    path('add-to-cart/<int:id>/', views.cart, name='add_to_cart'),

    path('cart', views.view_cart, name='view_cart'),
    path('cart/increase/<int:id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:id>/', views.decrease_quantity, name='decrease_quantity'),
    path('cart/remove/<int:id>/', views.remove_cart_item, name='remove_cart_item'),

    path('order-now', views.order_now_page, name='order_now_page'),
    path('order-now-submit', views.order_now, name='order_now'),
    path('order-success', views.order_success, name='order_success'),
    path('payment-success/',views. payment_success, name='payment_success'),
    path('get-cart-count', views.get_cart_count, name='get_cart_count'),
]
