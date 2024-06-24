from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from ShopNowApp.models import Product, Cart
from django.http import HttpResponseRedirect
from django.urls import reverse
from ShopNowApp.forms import CheckoutForm
from django.shortcuts import render, redirect, get_object_or_404
from ShopNowApp.models import Product, Cart, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
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
            user = form.get_user()
            login(request, user)
            return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def index(request):
    products = Product.objects.all()
    return render(request, 'index.html', {'products': products})

def pro(request):
    products = Product.objects.all()
    return render(request, 'products.html', {'products': products})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')


def cart(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
     cart_items = Cart.objects.filter(user=request.user)
     total_price = sum(item.total_price() for item in cart_items)
     return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def delete_from_cart(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    return redirect('cart')

def search_results(request):
    query = request.GET.get('q')
    results = []
    if query:
        results = Product.objects.filter(name__icontains=query)
    return render(request, 'search_results.html', {'results': results, 'query': query})

def order_history(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
     orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})



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
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart_items.delete()  # Clear the cart after checkout
            return redirect('order_history')
    else:
        form = CheckoutForm()
    return render(request, 'checkout.html', {'cart_items': cart_items, 'form': form})