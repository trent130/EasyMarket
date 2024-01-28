from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'staticpages/index.html')

def about(request):
    return render(request, 'staticpages/about.html')

def contact(request):
    return render(request, 'staticpages/contact.html')

def faq(request):
    return render(request, 'staticpages/faq.html')
