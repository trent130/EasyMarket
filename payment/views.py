from django.shortcuts import render

# Create your views here.
def payment_list(request):
    return render(request, 'payment/payment_list.html', {})