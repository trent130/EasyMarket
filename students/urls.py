from django.contrib import admin
from django.urls import path, include  

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('staticpages.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('products/', include('products.urls', namespace='products')),
    path('orders/', include('orders.urls')),
    path('payment/', include('payment.urls')),
    path('adminapp/', include('adminapp.urls')),
]