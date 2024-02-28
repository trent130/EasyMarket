from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from orders.models import Order
from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.mail import send_mail
from .forms import ContactForm

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




def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            send_mail(
                'Contact Form Submission from {}'.format(name),
                message,
                email,
                ['your-email@example.com'],  # Replace with your email
            )
            return redirect('marketplace:contact_success')
        else:
            # Form is not valid, so render the form with errors
            return render(request, 'staticpages/contact.html', {'form': form})
    else:
        form = ContactForm()
    return render(request, 'staticpages/contact.html', {'form': form})

def contact_success(request):   
    return render(request, 'staticpages/contact_success.html')

