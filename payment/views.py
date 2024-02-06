from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Transaction
from .forms import PaymentForm

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
            # Process the payment using Django-Pay
            # Update transaction status accordingly
            return redirect('payment_list')
        else:
            # Handle the case where the form is not valid
            pass
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

@login_required
def search_transactions(request):
    query = request.GET.get('q')
    user_transactions = Transaction.objects.filter(user=request.user, id__icontains=query)
    return render(request, 'payment/search_transactions.html', {'transactions': user_transactions, 'query': query})