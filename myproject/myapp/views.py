from django.shortcuts import render, redirect, get_object_or_404
from .models import Register, product, add_to_cart, Order, home, Coupon
from django.contrib import messages
import razorpay
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Count

# ================= BASIC PAGES =================

def landing(request):
    return render(request, 'landing_page.html')

def index(request):
    banner = home.objects.all()
    return render(request, 'index.html',{'banner':banner})

def collection(request):
    return render(request, 'collection.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


# ================= AUTH =================

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Register.objects.get(email=email)

            if user.password == password:
                # ✅ Login success
                request.session['email'] = email
                request.session['is_logged_in'] = True

                # ✅ Get pending cart data
                pending_product_id = request.session.pop('pending_cart_product', None)
                return_url = request.session.pop('return_url', '/')

                if pending_product_id:
                    return redirect('add_to_cart', pending_product_id)

                return redirect(return_url)

            else:
                messages.error(request, 'Incorrect Password')

        except Register.DoesNotExist:
            messages.error(request, 'Incorrect Email')

    return render(request, 'login.html')



def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_pass')

        if password != confirm_password:
            messages.error(request, 'Password do not match')
            return redirect('register')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters')
            return redirect('register')

        if Register.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('login')

        Register.objects.create(
            name=name,
            email=email,
            phone=phone,
            password=password,
            confirm_password=confirm_password
        )

        messages.success(request, 'Registered Successfully')
        return redirect('login')

    return render(request, 'register.html')


def logout(request):
    request.session.flush()
    return redirect('login')


def categories(request):
    selected_category = request.GET.get('category')

    if selected_category:
        view_product = product.objects.filter(product_Categorie=selected_category)
    else:
        view_product = product.objects.all()

    raw_counts = product.objects.values('product_Categorie').annotate(count=Count('id'))

    # 🔥 Convert to safe keys (no spaces)
    category_counts = {}
    for item in raw_counts:
        key = item['product_Categorie'].replace(" ", "_").lower()
        category_counts[key] = item['count']

    return render(request, 'categories.html', {
        'view_product': view_product,
        'selected_category': selected_category,
        'category_counts': category_counts,
        'total_count': product.objects.count()
    })

# ================= ADD TO CART =================

def cart(request, id):
    email = request.session.get('email')

    # ❌ NOT LOGGED IN
    if not email:
        request.session['pending_cart_product'] = id
        request.session['return_url'] = request.META.get('HTTP_REFERER', '/')
        return redirect('login')

    # ✅ LOGGED IN
    user = get_object_or_404(Register, email=email)
    product_obj = get_object_or_404(product, id=id)

    cart_item, created = add_to_cart.objects.get_or_create(
        user=user,
        add_to_cart_product=product_obj
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))



# ================= CART COUNT =================

def get_cart_count(request):
    email = request.session.get('email')
    if not email:
        return 0

    try:
        user = Register.objects.get(email=email)
        return add_to_cart.objects.filter(user=user).count()
    except Register.DoesNotExist:
        return 0


# ================= VIEW CART =================

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
    if not email:
        return redirect('login')

    user = Register.objects.get(email=email)
    item = get_object_or_404(add_to_cart, id=id, user=user)

    item.quantity += 1
    item.save()

    return redirect('view_cart')


def decrease_quantity(request, id):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    user = Register.objects.get(email=email)
    item = get_object_or_404(add_to_cart, id=id, user=user)

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

    user = Register.objects.get(email=email)
    item = get_object_or_404(add_to_cart, id=id, user=user)
    item.delete()

    return redirect('view_cart')


# ================= ORDER =================

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
    amount_paise = int(total_amount * 100)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    # Save details in session
    request.session['razorpay_order_id'] = razorpay_order['id']
    request.session['delivery_address'] = delivery_address
    request.session['delivery_date'] = delivery_date

    return render(request, "razorpay_payment.html", {
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "order_id": razorpay_order['id'],
        "amount": amount_paise,
        "total_amount": total_amount
    })
    

def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    params = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        client.utility.verify_payment_signature(params)

        email = request.session.get('email')
        user = Register.objects.get(email=email)
        cart_items = add_to_cart.objects.filter(user=user)

        total_amount = sum(item.total_price for item in cart_items)

        Order.objects.create(
            user=user,
            total_amount=total_amount,
            delivery_address=request.session.get('delivery_address'),
            delivery_date=request.session.get('delivery_date'),
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            payment_status="Paid",
            status="Confirmed"
        )

        cart_items.delete()
        return redirect('order_success')

    except:
        return HttpResponse("Payment Verification Failed")

def order_success(request):
    return render(request, 'order_success.html')
