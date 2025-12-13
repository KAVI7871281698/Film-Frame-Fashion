from django.shortcuts import render,redirect,get_object_or_404
from .models import Register,product,add_to_cart,Order
from django.contrib import messages
from django.db import transaction
from django.views.decorators.http import require_POST
# Create your views here.

def landing(request):
    return render(request,'landing_page.html')

def index(request):
    return render(request, 'index.html')

def collection(request):
    return render(request, 'collection.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def login(request):
    if request.method=='POST':
        email=request.POST['email']
        password=request.POST['password']

        try:
            take_data=Register.objects.get(email=email)
            if take_data.password==password:
                request.session['email']=email
                request.session['is_logged_in']=True
                return redirect('index')
            else:
                messages.error(request,'Incorrect Password')
        except:
            messages.error(request,'Incorrect Email')
            
    return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_pass')
        
        if password != confirm_password:
            messages.error(request,'Password do not match')
            return redirect('register')
            
        if len(password) < 6:  
            messages.error(request, "Password must be at least 6 characters")
            return redirect("register")
        
        if Register.objects.filter(email=email).exists():
            messages.error(request,'Email already exists')
            return redirect('login')
        
        database_save = Register(name=name,email=email,phone=phone,password=password,confirm_password=confirm_password)
        database_save.save()
        messages.success(request,'Registered Successfully')
        return redirect('login')
    
    return render(request, 'register.html')


def categories(request):
    view_product = product.objects.filter(product_Categorie='categorize1')
    return render(request, 'categories.html', {'view_product': view_product})


def cart(request, id):
    email = request.session.get('email')

    if not email:
        return redirect('login')

    user = get_object_or_404(Register, email=email)
    product_obj = get_object_or_404(product, id=id)

    cart_item, created = add_to_cart.objects.get_or_create(
        user=user,
        add_to_cart_product=product_obj
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # ✅ stay on same page
    return redirect(request.META.get('HTTP_REFERER', '/'))


def view_cart(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = Register.objects.get(email=email)

    cart_items = add_to_cart.objects.filter(user=user)

    total_amount = sum(item.total_price for item in cart_items)

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })
    
def increase_quantity(request, id):
    email = request.session.get('email')
    user = Register.objects.get(email=email)

    item = add_to_cart.objects.get(id=id, user=user)
    item.quantity += 1
    item.save()

    return redirect('view_cart')

def decrease_quantity(request, id):
    email = request.session.get('email')
    user = Register.objects.get(email=email)

    item = add_to_cart.objects.get(id=id, user=user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('view_cart')

def remove_cart_item(request, id):
    email = request.session.get('email')

    if not email:
        return redirect('login')

    user = get_object_or_404(Register, email=email)

    item = get_object_or_404(add_to_cart, id=id, user=user)
    item.delete()

    return redirect('view_cart')

def order_now_page(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = Register.objects.get(email=email)
    cart_items = add_to_cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('view_cart')

    total_amount = sum(item.total_price for item in cart_items)

    return render(request, 'order_now.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })
    

def order_now(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = Register.objects.get(email=email)
    cart_items = add_to_cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('view_cart')

    delivery_address = request.POST.get('delivery_address')
    delivery_date = request.POST.get('delivery_date')

    total_amount = sum(item.total_price for item in cart_items)

    Order.objects.create(
        user=user,
        total_amount=total_amount,
        delivery_address=delivery_address,
        delivery_date=delivery_date
    )

    cart_items.delete()

    return redirect('order_success')

def order_success(request):
    return render(request, 'order_success.html')

