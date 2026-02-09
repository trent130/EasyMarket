#!/usr/bin/env python
"""
Test script for Products API
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'students.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Student
from products.models import Product, Category
from decimal import Decimal

User = get_user_model()

def create_test_data():
    """Create test data for products"""
    print("Creating test data...")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'student'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✓ Created user: {user.email}")
    else:
        print(f"✓ User already exists: {user.email}")
    
    # Create student profile
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            'bio': 'Test student',
            'phone_number': '1234567890',
            'university': 'Test University'
        }
    )
    if created:
        print(f"✓ Created student profile for: {user.email}")
    else:
        print(f"✓ Student profile already exists for: {user.email}")
    
    # Create test category
    category, created = Category.objects.get_or_create(
        name='Electronics',
        defaults={
            'description': 'Electronic devices and accessories'
        }
    )
    if created:
        print(f"✓ Created category: {category.name}")
    else:
        print(f"✓ Category already exists: {category.name}")
    
    # Create test products
    products_data = [
        {
            'title': 'Laptop Dell XPS 13',
            'description': 'Excellent condition laptop, barely used',
            'price': Decimal('850.00'),
            'condition': 'like_new',
            'stock': 1
        },
        {
            'title': 'iPhone 12 Pro',
            'description': 'Great phone, no scratches',
            'price': Decimal('650.00'),
            'condition': 'good',
            'stock': 1
        },
        {
            'title': 'Wireless Mouse',
            'description': 'Logitech wireless mouse',
            'price': Decimal('25.00'),
            'condition': 'new',
            'stock': 5
        }
    ]
    
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            title=product_data['title'],
            student=student,
            defaults={
                **product_data,
                'category': category
            }
        )
        if created:
            print(f"✓ Created product: {product.title}")
        else:
            print(f"✓ Product already exists: {product.title}")
    
    print("\n✅ Test data created successfully!")
    print(f"\nTest credentials:")
    print(f"  Email: test@example.com")
    print(f"  Password: testpass123")
    print(f"\nTotal products: {Product.objects.count()}")
    print(f"Total categories: {Category.objects.count()}")

if __name__ == '__main__':
    create_test_data()
