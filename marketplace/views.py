from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from orders.models import Order
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.shortcuts import render
from .forms import searchForm
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

