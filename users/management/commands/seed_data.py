from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from users.models import UserProfile, Student
from products.models import Category, Product, Image
from marketplace.models import Cart, CartItem, WishList, WishListItem
from orders.models import Order, OrderItem
from staticpages.models import Address, ContactInfo, FooterLinks, Footer
from django.utils import timezone

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Seeds database with initial data for development'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')
        
        # Create users
        admin_user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='admin123',
            first_name='Admin',
            last_name='User',
            user_type='admin'
        )
        
        student1 = CustomUser.objects.create_user(
            email='student1@example.com',
            username='student1',
            password='student123',
            first_name='John',
            last_name='Doe',
            user_type='student'
        )
        
        student2 = CustomUser.objects.create_user(
            email='student2@example.com',
            username='student2',
            password='student123',
            first_name='Jane',
            last_name='Smith',
            user_type='student'
        )
        
        # Create profiles
        admin_profile = UserProfile.objects.create(
            user=admin_user,
            avatar='avatars/default.jpg'
        )
        
        student1_profile = UserProfile.objects.create(
            user=student1,
            avatar='avatars/default.jpg'
        )
        
        student2_profile = UserProfile.objects.create(
            user=student2,
            avatar='avatars/default.jpg'
        )
        
        # Create student models
        student1_model = Student.objects.create(
            user=student1,
            first_name='John',
            last_name='Doe',
            email='student1@example.com'
        )
        
        student2_model = Student.objects.create(
            user=student2,
            first_name='Jane',
            last_name='Smith',
            email='student2@example.com'
        )
        
        # Create categories
        textbooks = Category.objects.create(
            name='Textbooks',
            description='Academic textbooks for various courses'
        )
        
        electronics = Category.objects.create(
            name='Electronics',
            description='Laptops, phones, and other electronic devices'
        )
        
        furniture = Category.objects.create(
            name='Furniture',
            description='Dorm and apartment furniture'
        )
        
        clothing = Category.objects.create(
            name='Clothing',
            description='Used and new clothing items'
        )
        
        # Create products
        product1 = Product.objects.create(
            title='Introduction to Computer Science',
            description='Excellent condition textbook for CS101',
            price=45.99,
            category=textbooks
        )
        
        product2 = Product.objects.create(
            title='Used MacBook Pro 2019',
            description='13-inch, 8GB RAM, 256GB SSD, good condition',
            price=799.99,
            category=electronics
        )
        
        product3 = Product.objects.create(
            title='Desk Lamp',
            description='Adjustable LED desk lamp, barely used',
            price=24.50,
            category=furniture
        )
        
        product4 = Product.objects.create(
            title='University Hoodie',
            description='Size L, university logo, worn only a few times',
            price=35.00,
            category=clothing
        )
        
        # Create images
        image1 = Image.objects.create(
            product=product1,
            image='products/textbook1.jpg',
            description='Front cover of CS textbook'
        )
        
        image2 = Image.objects.create(
            product=product2,
            image='products/macbook.jpg',
            description='MacBook Pro front view'
        )
        
        image3 = Image.objects.create(
            product=product3,
            image='products/lamp.jpg',
            description='Desk lamp'
        )
        
        image4 = Image.objects.create(
            product=product4,
            image='products/hoodie.jpg',
            description='University hoodie front view'
        )
        
        # Create cart and items
        cart1 = Cart.objects.create(
            user=student1
        )
        
        cart_item1 = CartItem.objects.create(
            cart=cart1,
            product=product3,
            quantity=1
        )
        
        cart_item2 = CartItem.objects.create(
            cart=cart1,
            product=product4,
            quantity=2
        )
        
        # Create wishlist and items
        wishlist1 = WishList.objects.create(
            user=student1
        )
        
        wishlist_item1 = WishListItem.objects.create(
            wishlist=wishlist1,
            product=product1
        )
        
        wishlist_item2 = WishListItem.objects.create(
            wishlist=wishlist1,
            product=product2
        )
        
        # Create order and items
        order1 = Order.objects.create(
            user=student1,
            total_amount=94.50,
            status='completed'
        )
        
        order_item1 = OrderItem.objects.create(
            order=order1,
            product=product3,
            quantity=1,
            price=24.50
        )
        
        order_item2 = OrderItem.objects.create(
            order=order1,
            product=product4,
            quantity=2,
            price=35.00
        )
        
        # Create static pages data
        address = Address.objects.create(
            street='123 University Ave',
            city='College Town',
            state='CA',
            zip_code='90210',
            country='USA'
        )
        
        contact_info = ContactInfo.objects.create(
            address=address,
            phone='555-123-4567',
            email='contact@easymarket.com'
        )
        
        footer_links = FooterLinks.objects.create(
            title='Quick Links',
            url='#'
        )
        
        footer = Footer.objects.create(
            quickLinks=footer_links,
            contactInfo=contact_info
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))