from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from payments import get_payment_model
from .models import Transaction
from products.models import Product
from .forms import PaymentForm
from django_daraja.mpesa.core import MpesaClient
import csv
from django.http import HttpResponse
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

Payment = get_payment_model()

@login_required

def calculate_cart_total(request):
    total_price = Decimal(0)  # Initialize total_price as Decimal
    cart = request.session.get('cart', {})
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, pk=product_id)
        total_price += product.price * quantity
    return float(total_price)  # Convert Decimal to float before returning


@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))  # Parse JSON data
            logger.info("Mpesa Callback Data: %s", data)

            payment_status = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
            checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')

            transaction = get_object_or_404(Transaction, transaction_id=checkout_request_id)

            if payment_status == 0:  # 0 indicates success
                transaction.status = 'completed'
            else:
                transaction.status = 'failed'
            transaction.save()

            return HttpResponse(status=200)
        except Exception as e:
            logger.error("Error in mpesa_callback: %s", e)
            return HttpResponse(status=400)
    return HttpResponse(status=405)


@login_required
def payment_list(request):
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(user_transactions, 10)  # Show 10 transactions per page
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(request, 'payment/payment_list.html', {'transactions': transactions})



# Configure logging
logger = logging.getLogger(__name__)

@login_required
def make_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                cl = MpesaClient(
                    consumer_key=settings.MPESA_CONSUMER_KEY,
                    consumer_secret=settings.MPESA_CONSUMER_SECRET,
                    shortcode=settings.MPESA_SHORTCODE,
                    passkey=settings.MPESA_PASSKEY,
                    environment='sandbox'  # or 'production' if in production environment
                )

                phone_number = form.cleaned_data['phone_number']
                amount = int(calculate_cart_total(request))

                if amount <= 0:
                    raise ValueError("Cart total must be greater than zero")

                account_reference = form.cleaned_data['account_reference']
                transaction_desc = form.cleaned_data['transaction_desc']
                callback_url = settings.MPESA_CALLBACK_URL

                stk_response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
                logger.info("STK Push Response: %s", stk_response)

                if 'ResponseCode' in stk_response and stk_response['ResponseCode'] == '0':
                    transaction = Transaction.objects.create(
                        user=request.user,
                        amount=amount,
                        status='pending',
                        phone_number=phone_number,
                        account_reference=account_reference,
                        transaction_desc=transaction_desc,
                        transaction_id=stk_response.get('CheckoutRequestID', 'N/A')
                    )
                    return redirect('payment_process', token=transaction.pk)
                else:
                    raise Exception(f"Failed to initiate STK push: {stk_response}")

            except Exception as e:
                error_message = f"An error occurred while processing your transaction: {str(e)}"
                form.add_error(None, error_message)
                logger.error(error_message)

    else:
        cart_total = calculate_cart_total(request)
        if cart_total <= 0:
            return HttpResponse("Cannot proceed with zero cart total")

        request.session['cart_total'] = cart_total
        initial = {'amount': cart_total}
        form = PaymentForm(initial=initial)

    return render(request, 'payment/make_payment.html', {'form': form})

@login_required
def transaction_history(request):
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(user_transactions, 10)  # Show 10 transactions per page
    page = request.GET.get('page')
    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    return render(request, 'payment/transaction_history.html', {'transactions': transactions})

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    return render(request, 'payment/transaction_detail.html', {'transaction': transaction})

@login_required
def export_transactions(request):
    user_transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    # Generate CSV file and return as HTTP response
    # Code for exporting transactions to CSV format
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment; filename = "transactions.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Transaction ID', 'User', 'Amount', 'Timestamp', 'Status'])
    
    for transaction in user_transactions:
        writer.writerow([Transaction.id, transaction.user.username, transaction.amount, transaction.timestamp, transaction.status])
    
    return response

@login_required
def search_transactions(request):
    query = request.GET.get('q')
    user_transactions = Transaction.objects.filter(user=request.user, id__icontains=query)
    return render(request, 'payment/search_transactions.html', {'transactions': user_transactions, 'query': query})

@login_required
def payment_process(request, token):
    transaction = get_object_or_404(Transaction, pk=token)
    return render(request, 'payment/payment_process.html', {'transaction': transaction})
