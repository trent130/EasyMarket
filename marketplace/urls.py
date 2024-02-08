from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # path('', views.index, name='home'),
    path('chat_room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('typing_status/', views.typing_status, name='typing_status'),
]