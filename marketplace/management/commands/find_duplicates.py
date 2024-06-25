from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from marketplace.models import WishList

class Command(BaseCommand):
    help = "Find dublicate wishlist objects"
    
    def handle(self, *args, **kwargs):
        users = User.objects.all()
        for user in users:
            wishlist = WishList.objects.filter(user=user)
        
            if wishlist.count() > 1:
                print(f"{user.username} has {wishlist.count() } wishlists")