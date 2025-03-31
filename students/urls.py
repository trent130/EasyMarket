from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    re_path(r"^static/(?P<path>.*)", serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path('', include('staticpages.urls')),
    path('api/v1/marketplace/', include('marketplace.urls')),
    path('api/v1/products/', include('products.urls', namespace='products')),
    path('api/v1/orders/', include('orders.urls')),
    path('api/v1/payment/', include('payment.urls')),
    path('api/v1/admin/', include('adminapp.urls')),
    path('api/v1/users/', include('users.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
