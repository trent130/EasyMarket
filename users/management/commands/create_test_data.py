from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

# Import models
from users.models import UserProfile, Student
from products.models import Category, Product, ProductVariant
from marketplace.models import Cart, CartItem, WishList, Review
from orders.models import Order, OrderItem, ShippingAddress
from payment.models import Transaction

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Creates comprehensive test data for development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before creating new test data',
        )

    def handle(self, *args, **kwargs):
        if kwargs['clear']:
            self.clear_data()

        self.create_users()
        self.create_categories()
        self.create_products()
        self.create_product_variants()
        self.create_marketplace_data()
        self.create_orders()
        self.create_transactions()

        self.stdout.write(self.style.SUCCESS('Successfully created comprehensive test data'))
        self.stdout.write("\nTest accounts available:")
        self.stdout.write("   Admin: admin@example.com / admin123")
        self.stdout.write("   Student: john.doe@student.edu / student123")
        self.stdout.write("   Customer: customer1@example.com / customer123")

    def clear_data(self):
        """Clear existing test data"""
        self.stdout.write('Clearing existing data...')

        # Clear in reverse dependency order
        Transaction.objects.all().delete()
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        ShippingAddress.objects.all().delete()
        Review.objects.all().delete()
        CartItem.objects.all().delete()
        Cart.objects.all().delete()
        WishList.objects.all().delete()
        ProductVariant.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Student.objects.all().delete()
        UserProfile.objects.all().delete()
        CustomUser.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Data cleared successfully'))

    def create_users(self):
        """Create test users"""
        self.stdout.write('Creating users...')

        # Create admin user (or get existing one)
        self.admin, created = CustomUser.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            self.admin.set_password('admin123')
            self.admin.save()

        # Create student users
        students_data = [
            {
                'email': 'john.doe@student.edu',
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'bio': 'Computer Science major, love coding and tech gadgets.'
            },
            {
                'email': 'jane.smith@student.edu',
                'username': 'janesmith',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'bio': 'Business major, interested in entrepreneurship.'
            },
            {
                'email': 'mike.wilson@student.edu',
                'username': 'mikewilson',
                'first_name': 'Mike',
                'last_name': 'Wilson',
                'bio': 'Engineering student, selling old textbooks and equipment.'
            },
            {
                'email': 'sarah.brown@student.edu',
                'username': 'sarahbrown',
                'first_name': 'Sarah',
                'last_name': 'Brown',
                'bio': 'Art major, love creative projects and design.'
            },
            {
                'email': 'alex.johnson@student.edu',
                'username': 'alexjohnson',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'bio': 'Psychology major, interested in human behavior.'
            }
        ]

        self.students = []
        for student_data in students_data:
            user, created = CustomUser.objects.get_or_create(
                username=student_data['username'],
                defaults={
                    'email': student_data['email'],
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'user_type': 'student'
                }
            )
            if created:
                user.set_password('student123')
                user.save()

            # Update the Student profile created by signal
            student_profile, _ = Student.objects.get_or_create(user=user)
            student_profile.bio = student_data['bio']
            student_profile.save()

            self.students.append(user)

        # Create customer users
        customers_data = [
            {
                'email': 'customer1@example.com',
                'username': 'customer1',
                'first_name': 'Robert',
                'last_name': 'Davis',
            },
            {
                'email': 'customer2@example.com',
                'username': 'customer2',
                'first_name': 'Emily',
                'last_name': 'Taylor',
            }
        ]

        self.customers = []
        for customer_data in customers_data:
            user, created = CustomUser.objects.get_or_create(
                username=customer_data['username'],
                defaults={
                    'email': customer_data['email'],
                    'first_name': customer_data['first_name'],
                    'last_name': customer_data['last_name'],
                    'user_type': 'customer'
                }
            )
            if created:
                user.set_password('customer123')
                user.save()
            self.customers.append(user)

        self.stdout.write(f'Created {len(self.students)} students and {len(self.customers)} customers')

    def create_categories(self):
        """Create product categories"""
        self.stdout.write('Creating categories...')

        categories_data = [
            {
                'name': 'Textbooks',
                'description': 'Academic textbooks for various courses and subjects'
            },
            {
                'name': 'Electronics',
                'description': 'Laptops, phones, tablets, and other electronic devices'
            },
            {
                'name': 'Furniture',
                'description': 'Dorm and apartment furniture, desks, chairs, storage'
            },
            {
                'name': 'Clothing',
                'description': 'Used and new clothing items, university merchandise'
            },
            {
                'name': 'Sports & Recreation',
                'description': 'Sports equipment, gym gear, recreational items'
            },
            {
                'name': 'School Supplies',
                'description': 'Notebooks, pens, calculators, and other school essentials'
            },
            {
                'name': 'Kitchen & Appliances',
                'description': 'Small appliances, cookware, and kitchen essentials'
            }
        ]

        self.categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            self.categories.append(category)

        self.stdout.write(f'Created {len(self.categories)} categories')

    def create_products(self):
        """Create test products"""
        self.stdout.write('Creating products...')

        products_data = [
            # Textbooks
            {
                'title': 'Introduction to Computer Science (10th Edition)',
                'description': 'Comprehensive textbook for CS101. Excellent condition, minimal highlighting. Perfect for beginners learning programming fundamentals.',
                'price': Decimal('89.99'),
                'category': 0,  # Textbooks
                'condition': 'like_new',
                'stock': 1,
                'student_index': 0,  # John Doe
                'featured': True
            },
            {
                'title': 'Calculus: Early Transcendentals',
                'description': 'Essential calculus textbook for engineering and math students. Some wear but all pages intact.',
                'price': Decimal('125.50'),
                'category': 0,  # Textbooks
                'condition': 'good',
                'stock': 1,
                'student_index': 2,  # Mike Wilson
                'featured': False
            },
            {
                'title': 'Principles of Economics (8th Edition)',
                'description': 'Microeconomics and macroeconomics fundamentals. Great for business students.',
                'price': Decimal('95.00'),
                'category': 0,  # Textbooks
                'condition': 'good',
                'stock': 2,
                'student_index': 1,  # Jane Smith
                'featured': True
            },

            # Electronics
            {
                'title': 'MacBook Pro 13" 2020 (M1 Chip)',
                'description': '8GB RAM, 256GB SSD. Excellent condition, barely used. Includes original charger and box.',
                'price': Decimal('899.99'),
                'category': 1,  # Electronics
                'condition': 'like_new',
                'stock': 1,
                'student_index': 0,  # John Doe
                'featured': True
            },
            {
                'title': 'iPad Air (4th Generation)',
                'description': '64GB WiFi model in space gray. Perfect for note-taking and digital art.',
                'price': Decimal('450.00'),
                'category': 1,  # Electronics
                'condition': 'good',
                'stock': 1,
                'student_index': 3,  # Sarah Brown
                'featured': False
            },
            {
                'title': 'iPhone 12 - 128GB',
                'description': 'Unlocked, excellent condition. Screen protector applied since day one.',
                'price': Decimal('520.00'),
                'category': 1,  # Electronics
                'condition': 'like_new',
                'stock': 1,
                'student_index': 4,  # Alex Johnson
                'featured': False
            },

            # Furniture
            {
                'title': 'IKEA Desk with Drawers',
                'description': 'White desk perfect for dorm room. Some minor scratches but very functional.',
                'price': Decimal('75.00'),
                'category': 2,  # Furniture
                'condition': 'good',
                'stock': 1,
                'student_index': 2,  # Mike Wilson
                'featured': False
            },
            {
                'title': 'Ergonomic Office Chair',
                'description': 'Comfortable chair for long study sessions. Adjustable height and lumbar support.',
                'price': Decimal('120.00'),
                'category': 2,  # Furniture
                'condition': 'good',
                'stock': 1,
                'student_index': 1,  # Jane Smith
                'featured': False
            },

            # Clothing
            {
                'title': 'University Hoodie - Large',
                'description': 'Official university merchandise. Navy blue, size Large. Worn a few times.',
                'price': Decimal('35.00'),
                'category': 3,  # Clothing
                'condition': 'like_new',
                'stock': 3,
                'student_index': 0,  # John Doe
                'featured': False
            },
            {
                'title': 'Winter Jacket - Medium',
                'description': 'Warm winter jacket, perfect for cold campus walks. Black, size Medium.',
                'price': Decimal('60.00'),
                'category': 3,  # Clothing
                'condition': 'good',
                'stock': 1,
                'student_index': 3,  # Sarah Brown
                'featured': False
            },

            # Sports & Recreation
            {
                'title': 'Tennis Racket with Case',
                'description': 'Wilson tennis racket in great condition. Includes protective case.',
                'price': Decimal('45.00'),
                'category': 4,  # Sports & Recreation
                'condition': 'good',
                'stock': 1,
                'student_index': 4,  # Alex Johnson
                'featured': False
            },
            {
                'title': 'Yoga Mat - Premium',
                'description': 'High-quality yoga mat, barely used. Perfect for dorm room workouts.',
                'price': Decimal('25.00'),
                'category': 4,  # Sports & Recreation
                'condition': 'like_new',
                'stock': 2,
                'student_index': 3,  # Sarah Brown
                'featured': False
            },

            # School Supplies
            {
                'title': 'Scientific Calculator - TI-84 Plus',
                'description': 'Essential calculator for math and science courses. Excellent condition.',
                'price': Decimal('85.00'),
                'category': 5,  # School Supplies
                'condition': 'like_new',
                'stock': 1,
                'student_index': 2,  # Mike Wilson
                'featured': True
            },
            {
                'title': 'Art Supply Set',
                'description': 'Complete set of colored pencils, markers, and sketchbooks. Perfect for art students.',
                'price': Decimal('40.00'),
                'category': 5,  # School Supplies
                'condition': 'new',
                'stock': 1,
                'student_index': 3,  # Sarah Brown
                'featured': False
            },

            # Kitchen & Appliances
            {
                'title': 'Mini Fridge - Compact',
                'description': 'Perfect for dorm room. Energy efficient and quiet operation.',
                'price': Decimal('150.00'),
                'category': 6,  # Kitchen & Appliances
                'condition': 'good',
                'stock': 1,
                'student_index': 1,  # Jane Smith
                'featured': False
            },
            {
                'title': 'Coffee Maker - Single Serve',
                'description': 'Keurig-compatible single serve coffee maker. Essential for early morning classes.',
                'price': Decimal('65.00'),
                'category': 6,  # Kitchen & Appliances
                'condition': 'like_new',
                'stock': 1,
                'student_index': 0,  # John Doe
                'featured': False
            }
        ]

        self.products = []
        for product_data in products_data:
            # Get the student who owns this product
            student_user = self.students[product_data['student_index']]
            student_profile = Student.objects.get(user=student_user)

            product, created = Product.objects.get_or_create(
                title=product_data['title'],
                student=student_profile,
                defaults={
                    'description': product_data['description'],
                    'price': product_data['price'],
                    'category': self.categories[product_data['category']],
                    'condition': product_data['condition'],
                    'stock': product_data['stock'],
                    'featured': product_data['featured'],
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 30))
                }
            )
            self.products.append(product)

        self.stdout.write(f'Created {len(self.products)} products')

    def create_product_variants(self):
        """Create product variants for some products"""
        self.stdout.write('Creating product variants...')

        # Add variants for the university hoodie (different sizes)
        hoodie_product = None
        for product in self.products:
            if 'University Hoodie' in product.title:
                hoodie_product = product
                break

        if hoodie_product:
            variants_data = [
                {'name': 'Small', 'sku': 'UNI-HOODIE-S', 'price_adjustment': Decimal('-5.00'), 'stock': 2},
                {'name': 'Medium', 'sku': 'UNI-HOODIE-M', 'price_adjustment': Decimal('0.00'), 'stock': 3},
                {'name': 'Large', 'sku': 'UNI-HOODIE-L', 'price_adjustment': Decimal('0.00'), 'stock': 1},
                {'name': 'X-Large', 'sku': 'UNI-HOODIE-XL', 'price_adjustment': Decimal('5.00'), 'stock': 1},
            ]

            for variant_data in variants_data:
                variant, created = ProductVariant.objects.get_or_create(
                    sku=variant_data['sku'],
                    defaults={
                        'name': variant_data['name'],
                        'price_adjustment': variant_data['price_adjustment'],
                        'stock': variant_data['stock']
                    }
                )
                hoodie_product.variants.add(variant)

        self.stdout.write('Created product variants')

    def create_marketplace_data(self):
        """Create marketplace data like carts, wishlists, and reviews"""
        self.stdout.write('Creating marketplace data...')

        # Create carts for some users
        for user in self.students[:3]:  # First 3 students get carts
            cart, created = Cart.objects.get_or_create(
                user=user,
                defaults={'slug': f'cart-{user.username}'}
            )

            # Add some random products to cart
            available_products = random.sample(self.products, min(3, len(self.products)))
            for product in available_products:
                if random.choice([True, False]):  # 50% chance to add to cart
                    CartItem.objects.create(
                        cart=cart,
                        product=product,
                        quantity=random.randint(1, 2)
                    )

        # Create wishlists for some users
        for user in self.students:
            wishlist, created = WishList.objects.get_or_create(user=user)

            # Add some random products to wishlist
            available_products = random.sample(self.products, min(4, len(self.products)))
            for product in available_products:
                if random.choice([True, False]):  # 50% chance to add to wishlist
                    wishlist.products.add(product)

        # Create reviews for some products
        review_data = [
            {
                'product_index': 0,  # CS Textbook
                'reviewer_index': 1,  # Jane Smith
                'rating': 5,
                'comment': 'Excellent textbook! Really helped me understand the fundamentals of computer science.'
            },
            {
                'product_index': 3,  # MacBook Pro
                'reviewer_index': 2,  # Mike Wilson
                'rating': 5,
                'comment': 'Amazing laptop, exactly as described. Fast shipping and great communication from seller.'
            },
            {
                'product_index': 12,  # Calculator
                'reviewer_index': 4,  # Alex Johnson
                'rating': 4,
                'comment': 'Good calculator, works perfectly. Minor scratches but doesn\'t affect functionality.'
            },
            {
                'product_index': 1,  # Calculus book
                'reviewer_index': 0,  # John Doe
                'rating': 4,
                'comment': 'Helpful book for calculus class. Some highlighting but still very readable.'
            }
        ]

        for review_info in review_data:
            Review.objects.get_or_create(
                product=self.products[review_info['product_index']],
                reviewer=self.students[review_info['reviewer_index']],
                defaults={
                    'rating': review_info['rating'],
                    'comment': review_info['comment'],
                    'timestamp': timezone.now() - timedelta(days=random.randint(1, 15))
                }
            )

        self.stdout.write('Created marketplace data (carts, wishlists, reviews)')

    def create_orders(self):
        """Create test orders"""
        self.stdout.write('Creating orders...')

        # Create shipping addresses for customers
        shipping_addresses = []
        address_data = [
            {
                'user_index': 0,  # First customer
                'first_name': 'Robert',
                'last_name': 'Davis',
                'email': 'customer1@example.com',
                'phone': '555-123-4567',
                'address': '123 Main Street, Apt 4B',
                'city': 'College Town',
                'postal_code': '12345'
            },
            {
                'user_index': 1,  # Second customer
                'first_name': 'Emily',
                'last_name': 'Taylor',
                'email': 'customer2@example.com',
                'phone': '555-987-6543',
                'address': '456 University Ave',
                'city': 'College Town',
                'postal_code': '12346'
            }
        ]

        for addr_data in address_data:
            address = ShippingAddress.objects.create(
                user=self.customers[addr_data['user_index']],
                first_name=addr_data['first_name'],
                last_name=addr_data['last_name'],
                email=addr_data['email'],
                phone=addr_data['phone'],
                address=addr_data['address'],
                city=addr_data['city'],
                postal_code=addr_data['postal_code'],
                is_default=True
            )
            shipping_addresses.append(address)

        # Create orders
        orders_data = [
            {
                'user_index': 0,  # First customer
                'address_index': 0,
                'status': 'delivered',
                'payment_method': 'MPESA',
                'payment_status': True,
                'products': [
                    {'product_index': 0, 'quantity': 1},  # CS Textbook
                    {'product_index': 13, 'quantity': 1}  # Art Supply Set
                ],
                'days_ago': 10
            },
            {
                'user_index': 1,  # Second customer
                'address_index': 1,
                'status': 'shipped',
                'payment_method': 'CASH',
                'payment_status': False,
                'products': [
                    {'product_index': 6, 'quantity': 1},  # IKEA Desk
                    {'product_index': 11, 'quantity': 2}  # Yoga Mat
                ],
                'days_ago': 3
            },
            {
                'user_index': 0,  # First customer again
                'address_index': 0,
                'status': 'processing',
                'payment_method': 'MPESA',
                'payment_status': True,
                'products': [
                    {'product_index': 4, 'quantity': 1}  # iPad Air
                ],
                'days_ago': 1
            }
        ]

        self.orders = []
        for order_data in orders_data:
            # Calculate total amount
            total_amount = Decimal('0.00')
            for item in order_data['products']:
                product = self.products[item['product_index']]
                total_amount += product.price * item['quantity']

            order = Order.objects.create(
                user=self.customers[order_data['user_index']],
                reference=f"ORD-{random.randint(100000, 999999)}",
                shipping_address=shipping_addresses[order_data['address_index']],
                total_amount=total_amount,
                status=order_data['status'],
                payment_method=order_data['payment_method'],
                payment_status=order_data['payment_status'],
                notes='Test order created by fixture',
                created_at=timezone.now() - timedelta(days=order_data['days_ago'])
            )

            # Create order items
            for item in order_data['products']:
                product = self.products[item['product_index']]
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price
                )

            self.orders.append(order)

        self.stdout.write(f'Created {len(self.orders)} orders with items')

    def create_transactions(self):
        """Create test payment transactions"""
        self.stdout.write('Creating transactions...')

        transactions_data = [
            {
                'user_index': 0,  # First customer
                'amount': Decimal('129.99'),
                'phone_number': '254712345678',
                'status': 'completed',
                'payment_method': 'MPESA',
                'days_ago': 10
            },
            {
                'user_index': 0,  # First customer
                'amount': Decimal('450.00'),
                'phone_number': '254712345678',
                'status': 'completed',
                'payment_method': 'MPESA',
                'days_ago': 1
            },
            {
                'user_index': 1,  # Second customer
                'amount': Decimal('170.00'),
                'phone_number': '254798765432',
                'status': 'pending',
                'payment_method': 'CASH',
                'days_ago': 3
            }
        ]

        for trans_data in transactions_data:
            Transaction.objects.create(
                transaction_id=f"TXN-{random.randint(1000000, 9999999)}",
                merchant_request_id=f"MR-{random.randint(100000, 999999)}",
                payment_method=trans_data['payment_method'],
                user=self.customers[trans_data['user_index']],
                amount=trans_data['amount'],
                phone_number=trans_data['phone_number'],
                reference=f"REF-{random.randint(100000, 999999)}",
                description='Payment for marketplace order',
                checkout_request_id=f"CR-{random.randint(100000, 999999)}",
                status=trans_data['status'],
                timestamp=timezone.now() - timedelta(days=trans_data['days_ago'])
            )

        self.stdout.write(f'Created {len(transactions_data)} transactions')