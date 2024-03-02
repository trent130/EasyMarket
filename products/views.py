from django.shortcuts import render

def product(request, id, slug):
    context = {'title': 'product'}
    return render(request, 'products/product.html', context)

def product_list(request):
    context = {'title': 'product list'}
    return render(request, 'products/product_list.html', context)

def product_detail(request, id, slug):
    context = {'title': 'product detail'}
    return render(request, 'products/product_detail.html', context)


# Path: products/views.py
# Compare this snippet from staticpages/urls.py: