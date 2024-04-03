from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product
from .forms import ProductForm, ImageForm, CategoryForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from .models import Category,Image
from marketplace.models import Student
from django.forms import modelformset_factory

def product(request, id, slug):
    product = Product.objects.get(id=id)
    images = product.images.all()
    context = {'title': 'product', 'product': product, 'images': images}
    return render(request, 'products/product.html', context)

def product_list(request):
    product_list = Product.objects.filter(is_active=True)
    paginator = Paginator(product_list, 12)  # Show 12 products per page.

    url = reverse('products:product_list')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {'page_obj': page_obj})

@login_required
def product_detail(request, id, slug):
    context = {'title': 'product detail'}
    product = Product.objects.get(id=id)  
    
    url = reverse('products:product_detail', args=[product.id, product.slug])
    product_detail_url = reverse('product_detail', args=[product.id, product.slug])
    return render(request, 'products/product_detail.html', context)


import logging

logger = logging.getLogger(__name__)

@login_required
def add_product(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, extra=1)

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())

        if product_form.is_valid() and formset.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            product.save()

            for form in formset.cleaned_data:
                if form:
                    image = form['image']
                    description = form['description']
                    Image.objects.create(product=product, image=image, description=description)

            return HttpResponseRedirect(reverse('products:product_list'))
        else:
            logger.error("Product form or formset is invalid")
            logger.error(product_form.errors)
            logger.error(formset.errors)
    else:
        product_form = ProductForm()
        formset = ImageFormSet(queryset=Image.objects.none())

    categories = Category.objects.all()  # Query for all categories

    return render(request, 'products/add_product.html', {'product_form': product_form, 'formset': formset, 'categories': categories})


@login_required
def user_products(request, user_id):
    url = reverse('products:user_product_list', args=[user_id])
    
    try:
        student = Student.objects.get(user=request.user)
        products = Product.objects.filter(student=student)
    except Student.DoesNotExist:
        # Handle the case where the user is not associated with a Student instance
        products = Product.objects.none()

    return render(request, 'products/product.html', {'products': products})

def category(request):
    categories = Category.objects.all()
    return render(request, 'staticpages/categories.html', {'categories' : categories})

