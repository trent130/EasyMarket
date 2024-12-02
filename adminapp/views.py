from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group, Permission
from django.contrib.admin.models import LogEntry
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from .forms import UserRoleForm

@login_required
class UserList(ListView):
    model = User
    template_name = 'pages/adminapp/user_list.html'

@login_required
class UserDetailView(DetailView):
    model = User
    template_name = 'pages/adminapp/user_detail.html'

@login_required
class UserDeleteView(DeleteView):
    model = User
    template_name = 'pages/adminapp/user_delete.html'
    success_url = reverse_lazy('user_list')

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
    return render(request, 'pages/adminapp/assign_role.html', {'form': form})

@login_required
class GroupListView(ListView):
    model = Group
    template_name = 'pages/adminapp/group_list.html'

@login_required
class GroupDetailView(DetailView):
    model = Group
    template_name = 'pages/adminapp/group_detail.html'

@login_required
class GroupDeleteView(DeleteView):
    model = Group
    template_name = 'pages/adminapp/group_delete.html'
    success_url = reverse_lazy('group_list')

@login_required
def user_activity_logs(request):
    logs = LogEntry.objects.all().order_by('-action_time')[:10]
    return render(request, 'pages/adminapp/user_activity_logs.html', {'logs': logs})

@login_required
def user_permissions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    permissions = Permission.objects.filter(user=user)
    return render(request, 'pages/adminapp/user_permissions.html', {'user': user, 'permissions': permissions})

@login_required
def group_permissions(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    permissions = Permission.objects.filter(group=group)
    return render(request, 'pages/adminapp/group_permissions.html', {'group': group, 'permissions': permissions})

@login_required
def admin_home(request):
    return render(request, 'pages/adminapp/admin_home.html')