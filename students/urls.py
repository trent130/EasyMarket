from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static 
from django.views.static import serve

urlpatterns = [
    re_path(r"^static/(?P<path>.*)", serve, {'document_root': settings.STATIC_ROOT}),
    re_path(r'^media/(?P<path>.*)', serve,  {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
   # path('api/', include('backend.api.urls')),  # Add API URLs
    path('', include('staticpages.urls')),
    path('marketplace/', include('marketplace.urls')),
    path('products/', include('products.urls', namespace='products')),
    path('orders/', include('orders.urls')),
    path('payment/', include('payment.urls')),
    path('adminapp/', include('adminapp.urls')),
]

if settings.DEBUG:
     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
