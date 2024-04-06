from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from payments import get_payment_model
from .models import Transaction
from .forms import PaymentForm
from django_daraja.mpesa.core import MpesaClient
import csv
from django.http import HttpResponse

Payment = get_payment_model()

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
def make_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
           try:
                # Process the payment using Mpesa
                cl = MpesaClient()
                phone_number = form.cleaned_data['phone_number']
                amount = form.cleaned_data['amount']
                account_reference = form.cleaned_data['account_reference']
                transaction_desc = form.cleaned_data['transaction_desc']
                callback_url = 'https://api.darajambili.com/express-payment'
            
                # Make the Mpesa API call
                response = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)
            
                # Create a Payment object (assuming you have appropriate fields in your model)
                payment = Payment.objects.create(
                amount=amount,
                status='Pending',  # Assuming there's a field for payment status
                # Add other fields as needed
                )
            
                # Update transaction status accordingly
                # Redirect to payment process page
                return redirect(reverse('payment_process', kwargs={'token': payment.token}))
           except Exception as e:
                error_message = "an error occured while processing your transaction"
                form.add_error(None, error_message)    
    else:
        form = PaymentForm()
    return render(request, 'payment/make_payment.html', {'form': form})

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
