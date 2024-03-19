from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product
from .forms import ProductForm, ImageForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from students.models import Student


def product(request, id, slug):
    product = Product.objects.get(id=id)
    images = product.images.all()
    context = {'title': 'product', 'product': product, 'images': images}
    return render(request, 'products/product.html', context)

def product_list(request):
    product_list = Product.objects.filter(is_active=True)
    paginator = Paginator(product_list, 12)  # Show 12 products per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {'page_obj': page_obj})

@login_required
def product_detail(request, id, slug):
    context = {'title': 'product detail'}
    product = Product.objects.get(id=id)  
    product_detail_url = reverse('product_detail', args=[product.id, product.slug])
    return render(request, 'products/product_detail.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)
        if product_form.is_valid() and image_form.is_valid():
            # save the forms...
            pass
    else:
        product_form = ProductForm()
        image_form = ImageForm()

    return render(request, 'products/add_product.html', {'product_form': product_form, 'image_form': image_form})

@login_required
def user_products(request, user_id):
    try:
        student = Student.objects.get(user=request.user)
        products = Product.objects.filter(student=student)
    except Student.DoesNotExist:
        # Handle the case where the user is not associated with a Student instance
        products = Product.objects.none()  # Returns an empty QuerySet

    return render(request, 'products/product.html', {'products': products})