from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_home, name='admin_home'),
    path('users/', views.UserList, name='user_list'),  # Changed UserListView.as_view() to user_list
    path('users/<int:pk>/', views.UserDetailView, name='user_detail'),
    path('users/<int:pk>/delete/', views.UserDeleteView, name='user_delete'),
    path('users/<int:pk>/assign_role/', views.assign_role, name='assign_role'),
    path('groups/', views.GroupListView, name='group_list'),
    path('groups/<int:pk>/', views.GroupDetailView, name='group_detail'),
    path('groups/<int:pk>/delete/', views.GroupDeleteView, name='group_delete'),
    path('activity_logs/', views.user_activity_logs, name='user_activity_logs'),
    path('users/<int:pk>/permissions/', views.user_permissions, name='user_permissions'),
    path('groups/<int:pk>/permissions/', views.group_permissions, name='group_permissions'),
]