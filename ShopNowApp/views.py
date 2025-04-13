from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from ShopNowApp.models import Product, Cart, Order, OrderItem
from ShopNowApp.forms import CheckoutForm


# ------------------ Auth Views ------------------

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


# ------------------ Product Views ------------------

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})


def pro(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


# ------------------ Cart Views ------------------

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.total_price() for item in cart_items)
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})


@login_required
def delete_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart')


# ------------------ Search & Order ------------------

def search_results(request):
    query = request.GET.get('q')
    results = Product.objects.filter(name__icontains=query) if query else []
    return render(request, 'search_results.html', {'results': results, 'query': query})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})


# ------------------ Checkout ------------------

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                total_price=sum(item.total_price() for item in cart_items),
                address=form.cleaned_data['address']
            )
            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                ) for item in cart_items
            ])
            cart_items.delete()
            return redirect('order_history')
    else:
        form = CheckoutForm()
    return render(request, 'checkout.html', {'cart_items': cart_items, 'form': form})


# ------------------ Newsletter Subscription ------------------

def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            message = f"""
            Hii {email}
            Welcome to the ShopNow family!
We’re beyond excited to have you on board. Your inbox just got a whole lot more exciting! 🥳

By subscribing to our newsletter, you've unlocked a gateway to:

🛍️ Early Access to fresh product launches

🎁 Exclusive Offers made just for you

⚡ Real-Time Updates on sales, deals, and trending items

💡 Expert Tips & Style Guides for smarter shopping

And because we’re feeling extra generous… here’s a special welcome treat:
🎉 Enjoy 10% OFF your first order!
Use code: WELCOME10 at checkout.
👉 Start Shopping Now

We’re here to make your shopping experience seamless, fun, and rewarding. Whether you’re browsing for the latest fashion, home upgrades, or everyday essentials, we’ve got everything you need — and then some!

If you ever have any questions, ideas, or just want to say hi — we’re all ears!
📧 Contact Support

Stay tuned! Exciting things are just around the corner.
Thanks again for joining us — and get ready to ShopNow like never before.

Happy Shopping!
— The ShopNow Team
            """
            mail = EmailMessage(
                subject="Welcome to ShopNow 🛒",
                body=message,
                from_email="rohitpatial121@gmail.com",
                to=[email],
                cc=["rohitpatial121@gmail.com"]
            )
            mail.send()
        return redirect("index")
