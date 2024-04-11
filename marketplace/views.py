from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from django.http import HttpResponseNotAllowed
from .forms import searchForm, AddToCartForm, UpdateCartForm, RemoveFromCartForm
from products.models import Product
from .models import CartItem, Cart

@login_required
def checkout(request):
    if request.method == 'POST':
        user = request.user

        # Create a new order
        order = Order(user=user)

        # Add the items from the cart to the order
        for item in user.cart.all():
            order.items.add(item)

        # Save the order
        order.save()

        # Clear the cart
        user.cart.clear()
        user.save()

        messages.success(request, "Checkout successful. Your order is being processed.")
        return redirect('marketplace:order_confirmation', order_id=order.id)

    else:
        # If the request method is not POST, redirect to the cart page
        return redirect('marketplace:cart')

def clear_cart(request): 
    if request.method == 'POST':
        user = request.user
        user.cart.clear()
        user.save()
        return redirect('marketplace:cart_cleared')
    else:
        return HttpResponseNotAllowed(['POST'])



# def cart_cleared(request):
#     return render(request, 'marketplace/cart_cleared.html')

def search(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed['GET']
    
    query = request.GET.get('q', '')
    results = Product.objects.filter(title__icontains=query)
 
    return render(request, 'marketplace/search_results.html', {'query': query, 'results': results})

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart = request.session.get('cart', {})
            if product_id in cart:
                # If the product is already in the cart, update its quantity
                cart[product_id] += quantity
            else:
                # If the product is not in the cart, add it
                cart[product_id] = quantity
            request.session['cart'] = cart
            messages.success(request, f"{product.title} added to cart")
            return redirect('marketplace:cart')
    else:
        form = AddToCartForm(initial={'product_id': product_id})
    return render(request, 'marketplace/add_to_cart.html', {'product': product, 'form': form})


def cart(request):
    cart_items = []
    total_price = 0
    cart = request.session.get('cart', {})
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        total_price += product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity, 'total': product.price * quantity})
    return render(request, 'marketplace/cart.html', {'cart_items': cart_items, 'cart_total': total_price})

def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = UpdateCartForm(request.POST)
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        cart = request.session.get('cart', {})
        if quantity > 0:
            cart[product_id] = quantity
            request.session['cart'] = cart
            messages.success(request, f"Quantity for {product.title} updated in cart")
        else:
            del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, f"{product.title} removed from cart")
    return redirect('marketplace:cart')  # <-- Corrected the redirect here


def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, f"{product.title} removed from cart")
    return redirect('marketplace:cart')

