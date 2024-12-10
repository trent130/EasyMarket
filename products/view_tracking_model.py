from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class ProductViewTrack(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
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
    ).order_by('?')[:4]  # Random selection
    
    serializer = self.get_serializer(recommendations, many=True)
    return Response(serializer.data)
"""