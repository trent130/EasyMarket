from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order
from django.http import HttpResponseNotAllowed
from .forms import searchForm, AddToCartForm, UpdateCartForm, RemoveFromCartForm
from products.models import Product
from .models import CartItem, Cart, WishList

# def cart_cleared(request):
#     return render(request, 'marketplace/cart_cleared.html')

def search(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed['GET']
    
    query = request.GET.get('q', '')
    results = Product.objects.filter(title__icontains=query)
 
    return render(request, 'pages/marketplace/search_results.html', {'query': query, 'results': results})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = AddToCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            cart = form.cleaned_data['cart', {}]
            current_quantity = cart.get(product_id, 0)

            if current_quantity + quantity > product.stock:
                messages.error(request, f"Not enough stock available for {product.title}.")
            else:
                cart[product_id] = current_quantity + quantity
                request.session['cart'] = cart
                messages.success(request, f"{product.title} added to cart")
                return redirect('marketplace:cart')
    else:
        form = AddToCartForm(initial={'product_id': product_id})
    return render(request, 'pages/marketplace/add_to_cart.html', {'product': product, 'form': form})



def cart(request):
    cart_items = []
    total_price = 0
    cart = request.session.get('cart', {})
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        total_price += product.price * quantity
        cart_items.append({'product': product, 'quantity': quantity, 'total': product.price * quantity})
    return render(request, 'pages/marketplace/cart.html', {'cart_items': cart_items, 'cart_total': total_price})

def update_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    form = UpdateCartForm(request.POST)
    if form.is_valid():
        quantity = form.cleaned_data['quantity']
        cart = request.session.get('cart', {})
        if quantity > 0:
            if quantity <= product.stock:
                cart[product_id] = quantity
                messages.success(request, f"Quantity for {product.title} updated in cart")
            else:
                messages.error(request, f"Not enough stock available for {product.title}.")
        else:
            if product_id in cart:
                del cart[product_id]
                messages.success(request, f"{product.title} removed from cart")
        request.session['cart'] = cart
    return redirect('pages/marketplace:cart')

def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        if product_id in cart:
            del cart[product_id]
            request.session['cart'] = cart
            messages.success(request, f"{product.title} removed from cart")
    return redirect('pages/marketplace:cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('pages/marketplace:cart')
    
    out_of_stock_items = []
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        if quantity > product.stock:
            out_of_stock_items.append(product.title)
    
    if out_of_stock_items:
        messages.error(request, f'The following items are out of stock: {", ".join(out_of_stock_items)}')
        return redirect('pages/marketplace:cart')
    
    # Deduct stock and clear cart items
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        product.stock -= quantity
        product.save()
    
    request.session['cart'] = {}
    messages.success(request, "Checkout successful. Your order is being processed.")
    return redirect('pages/marketplace:order_confirmation')  # Modify this redirect as needed


def clear_cart(request): 
    if request.method == 'POST':
        request.session['cart'] = {}
        messages.success(request, "Cart has been cleared.")
        return render(request, 'pages/marketplace/cart_cleared.html')
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = WishList.objects.get_or_create(user=request.user)
    wishlist.products.add(product)
    return redirect('pages/marketplace:wishlist_view')

@login_required
def wishlist_view(request):
    wishlist, created = WishList.objects.get_or_create(user=request.user)
    return render(request, 'pages/marketplace/wishlist.html', {'wishlist': wishlist})

@login_required
def remove_from_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(WishList, user=request.user)
    wishlist.products.remove(product)
    return redirect('pages/marketplace:wishlist_view')