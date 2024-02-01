from django.shortcuts import render

# Create your views here.
def adminapp_list(request):
    return render(request, 'adminapp/adminapp_list.html', {})

# def adminapp_detail(request):
#     return render(request, 'adminapp/adminapp_detail.html', {})

# def adminapp_create(request):
#     return render(request, 'adminapp/adminapp_create.html', {})

# def adminapp_update(request):
#     return render(request, 'adminapp/adminapp_update.html', {})

# def adminapp_delete(request):
#     return render(request, 'adminapp/adminapp_delete.html', {})


def admin_home(request):
    return render(request, 'adminapp/admin_home.html')