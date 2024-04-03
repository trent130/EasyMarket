from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from django.http import HttpResponseNotAllowed
from .forms import searchForm, AddToCartForm
from products.models import Product

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

def cart(request):
    return render(request, 'marketplace/cart.html')

def cart_cleared(request):
    return render(request, 'marketplace/cart_cleared.html')

def search(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed['GET']
    
    query = request.GET.get('q', '')
    results = Product.objects.filter(title__icontains=query)
    return render(request, 'marketplace/search_results.html', {'query': query, 'results': results})


def add_to_cart(request):
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data['product_id']
            quantity = form.cleaned_data['quantity']
            product = get_object_or_404(Product, id=product_id)
            user = request.user
            user.cart.add(product, through_defaults={'quantity': quantity})
            messages.success(request, f"{product.title} added to cart")
            return redirect('cart')  # Redirect to the cart view
        else:
            # Handle invalid form submission
            messages.error(request, "Invalid form submission")
            return redirect('home')  # Redirect to home page
    else:
        product_id = request.GET.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        form = AddToCartForm(initial={'product_id': product_id})
        return render(request, 'marketplace/add_to_cart.html', {'product': product, 'form': form})
