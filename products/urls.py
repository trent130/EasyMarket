from django.urls import path
from . import views

urlpatterns = [
    path('product/', views.product_list, name='product_list'),
    # other url patterns...
]