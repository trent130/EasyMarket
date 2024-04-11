from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Product
from products.forms import ProductForm, ImageForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Category,Image
from marketplace.models import Student


def product(request, id, slug):
    product = Product.objects.get(id=id)
    image = product.image.all()
    context = {'title': 'product', 'product': product, 'image': image}
    return render(request, 'products/product.html', context)


def product_list(request):
    product_list = Product.objects.prefetch_related('image').order_by('id')
    paginator = Paginator(product_list, 12)  # Show 12 products per page.

    url = reverse('products:product_list')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {'page_obj': page_obj})

@login_required
def product_detail(request, id, slug):
    try:
        product = get_object_or_404(Product, id=id, slug=slug)
        context = {'title': 'Product Detail', 'product': product}
        return render(request, 'products/product_detail.html', context)
    except Product.DoesNotExist:
        # Handle the case where the product doesn't exist
        return HttpResponse("Product not found", status=404)
    

@login_required
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        image_form = ImageForm(request.POST, request.FILES)  
        if product_form.is_valid() and image_form.is_valid():  
            product = product_form.save(commit=False)
            product.student = request.user.student 
            product.user = request.user
           
            category_id = request.POST.get('category')
            product.category_id = category_id
            
            product.save()
            print("product saved successfully")
            image = image_form.save(commit=False) 
            image.product = product
            image.save()
            
            return redirect('products:product_list') 
    else:
        product_form = ProductForm()
        image_form = ImageForm()
        
    categories = Category.objects.all()  
    return render(request, 'products/add_product.html', {'product_form': product_form, 'image_form': image_form, 'categories': categories})

@login_required
def user_products(request, user_id):
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
