from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product
from .forms import ProductForm, ImageForm
from django.urls import reverse


def product(request, id, slug):
    product = Product.objects.get(id=id)
    images = product.images.all()
    context = {'title': 'product', 'product': product, 'images': images}
    return render(request, 'products/product.html', context)

def product_list(request):
    product_list = Product.objects.filter(is_active=True)
    paginator = Paginator(product_list, 5)  # Show 5 products per page.

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
        product_form = ProductForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)  # handle uploaded files
        if product_form.is_valid() and image_form.is_valid():
            product = product_form.save()
            image = image_form.save(commit=False)
            image.product = product
            image.save()
            return redirect('product_list')
    else:
        product_form = ProductForm()
        image_form = ImageForm()
    return render(request, 'products/add_product.html', {'product_form': product_form, 'image_form': image_form})