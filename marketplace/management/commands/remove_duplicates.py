from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import WishList

class Command(BaseCommand):
    help = 'Remove duplicates'
    
    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user  in users:
            wishlist = WishList.objects.filter(user=user)
            if wishlist.count() > 1:
                primary_wishlist = wishlist.first()
                
                duplicates = wishlist.exclude(id=primary_wishlist.id)
                
                for duplicate in duplicates:
                    for product in duplicate.products.all():
                        primary_wishlist.products.add(product)    
                    duplicate.delete()
                
                print(f"{user.username}'s dublicates removed")