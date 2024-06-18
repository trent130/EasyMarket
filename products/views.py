from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Product
from products.forms import ProductForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Category
from marketplace.models import Student
from django.contrib import messages


def product(request, id, slug):
    product = Product.objects.get(id=id)
    context = {'title': 'product', 'product': product}
    return render(request, 'products/product.html', context)


def product_list(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 12)  # Show 12 products per page.

    url = reverse('products:product_list')
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'url':url}
    return render(request, 'products/product_list.html', context )

@login_required
def product_detail(request, id, slug):
    try:
        product = get_object_or_404(Product, id=id, slug=slug)
        reviews = Product.Review.all()
        reviews_count = reviews.Count()
        average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        
        context = {'title': 'Product Detail', 'product': product, 'reviews_count':reviews_count, 'average_rating':round(average_rating, 1)}
        return render(request, 'products/product_detail.html', context)
    except Product.DoesNotExist:
        # Handle the case where the product doesn't exist
        return HttpResponse("Product not found", status=404)
    

@login_required
def add_product(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES) 
        if product_form.is_valid():  
            product = product_form.save(commit=False)
            product.student = request.user.student 
            product.user = request.user
           
            category_id = request.POST.get('category')
            product.category_id = category_id

            product.save()
            messages.success(request, "product saved successfully")
            return redirect('products:product_list') 
    else:
        product_form = ProductForm()
        
    categories = Category.objects.all() 
    context =  {'product_form': product_form, 'categories': categories}
    return render(request, 'products/add_product.html', context)

@login_required
def user_products(request, user_id):
    try:
        student = Student.objects.get(user=request.user)
        products = Product.objects.filter(student=student)
        
        paginator = Paginator(products, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {'page_obj':page_obj, 'products': products}
        return render(request, 'products/product.html', context)
    
    except Student.DoesNotExist:
        # Handle the case where the user is not associated with a Student instance
        products = Product.objects.none()

   

def category(request):
    categories = Category.objects.all()
    return render(request, 'staticpages/categories.html', {'categories' : categories})
