from django.shortcuts import render

# # Create your views here.
# def adminapp_list(request):
#     return render(request, 'adminapp/adminapp_list.html', {})

# # def adminapp_detail(request):
# #     return render(request, 'adminapp/adminapp_detail.html', {})

# # def adminapp_create(request):
# #     return render(request, 'adminapp/adminapp_create.html', {})

# # def adminapp_update(request):
# #     return render(request, 'adminapp/adminapp_update.html', {})

# # def adminapp_delete(request):
# #     return render(request, 'adminapp/adminapp_delete.html', {})


# def admin_home(request):
#     return render(request, 'adminapp/admin_home.html')

# adminapp/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.models import LogEntry
from django.shortcuts import render, redirect, get_object_or_404
from .forms import UserRoleForm

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'adminapp/user_list.html', {'users': users})

@login_required
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'adminapp/user_detail.html', {'user': user})

@login_required
def user_delete(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.delete()
    return redirect('user_list')

@login_required
def assign_role(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserRoleForm(request.POST)
        if form.is_valid():
            group_name = form.cleaned_data['role']
            group = Group.objects.get(name=group_name)
            user.groups.clear()
            user.groups.add(group)
            return redirect('user_detail', user_id=user_id)
    else:
        form = UserRoleForm()
    return render(request, 'adminapp/assign_role.html', {'form': form})

@login_required
def group_list(request):
    groups = Group.objects.all()
    return render(request, 'adminapp/group_list.html', {'groups': groups})

@login_required
def group_detail(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    return render(request, 'adminapp/group_detail.html', {'group': group})

@login_required
def group_delete(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    group.delete()
    return redirect('group_list')

@login_required
def user_activity_logs(request):
    logs = LogEntry.objects.all().order_by('-action_time')[:10]
    return render(request, 'adminapp/user_activity_logs.html', {'logs': logs})

@login_required
def user_permissions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    permissions = Permission.objects.filter(user=user)
    return render(request, 'adminapp/user_permissions.html', {'user': user, 'permissions': permissions})

@login_required
def group_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    permissions = Permission.objects.filter(group=group)
    return render(request, 'adminapp/group_permissions.html', {'group': group, 'permissions': permissions})
