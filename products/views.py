from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product
from .forms import ProductForm
from django.urls import reverse


def product(request, id, slug):
    context = {'title': 'product'}
    return render(request, 'products/product.html', context)

def product_list(request):
    product_list = Product.objects.filter(is_active=True)
    paginator = Paginator(product_list, 7)  # Show 7 products per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {'page_obj': page_obj})

def product_detail(request, id, slug):
    context = {'title': 'product detail'}
    product = Product.objects.get(id=id)  
    product_detail_url = reverse('product_detail', args=[product.id, product.slug])
    return render(request, 'products/product_detail.html', context)

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'products/add_product.html', {'form': form})
# Path: products/views.py
# Compare this snippet from staticpages/urls.py: