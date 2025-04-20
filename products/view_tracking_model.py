from django.db import models
from users.model import CustomUser
from products.models import Product
from django.conf import settings


class ProductViewTrack(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user', 'ip_address')


"""
the view for the recommendation system will implement later
doing more research on the same still
# In views.py
@action(detail=True, methods=['get'])
def recommendations(self, request, slug=None):
    product = self.get_object()
    # Simple recommendation based on category and tags
    recommendations = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).order_by('?')[:4]  # Random selection of 4 products
    serializer = self.get_serializer(recommendations, many=True)
    return Response(serializer.data)
"""
