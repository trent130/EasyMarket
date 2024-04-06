from django.urls import path
from . import views

urlpatterns = [
    path('', views.payment_list, name='payment_list'),
    path('history/', views.transaction_history, name='transaction_history'),
    path('payment/', views.make_payment, name='make_payment'),
    path('transaction/<int:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    path('export/', views.export_transactions, name='export_transactions'),
    path('search/', views.search_transactions, name='search_transactions'),
]