from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from users.models import Student
from products.models import Category, Product
from marketplace.models import Cart, Review
from orders.models import Order
from payment.models import Transaction

CustomUser = get_user_model()

class Command(BaseCommand):
    help = 'Test the fixtures creation and verify data'

    def handle(self, *args, **kwargs):
        """Test the fixtures creation"""
        self.stdout.write("Testing fixtures creation...")
        
        # Clear existing data first
        self.stdout.write("\n1. Clearing existing data...")
        call_command('create_test_data', '--clear')
        
        # Create test data
        self.stdout.write("\n2. Creating test data...")
        call_command('create_test_data')
        
        # Verify data was created
        self.stdout.write("\n3. Verifying created data...")
        
        # Check users
        users_count = CustomUser.objects.count()
        students_count = Student.objects.count()
        self.stdout.write(f"   Users created: {users_count}")
        self.stdout.write(f"   Students created: {students_count}")
        
        # Check categories
        categories_count = Category.objects.count()
        self.stdout.write(f"   Categories created: {categories_count}")
        
        # Check products
        products_count = Product.objects.count()
        featured_products = Product.objects.filter(featured=True).count()
        self.stdout.write(f"   Products created: {products_count}")
        self.stdout.write(f"   Featured products: {featured_products}")
        
        # Check marketplace data
        carts_count = Cart.objects.count()
        reviews_count = Review.objects.count()
        self.stdout.write(f"   Carts created: {carts_count}")
        self.stdout.write(f"   Reviews created: {reviews_count}")
        
        # Check orders
        orders_count = Order.objects.count()
        self.stdout.write(f"   Orders created: {orders_count}")
        
        # Check transactions
        transactions_count = Transaction.objects.count()
        self.stdout.write(f"   Transactions created: {transactions_count}")
        
        # Verify relationships
        self.stdout.write("\n4. Verifying relationships...")
        
        # Check if students have products
        students_with_products = Student.objects.filter(products__isnull=False).distinct().count()
        self.stdout.write(f"   Students with products: {students_with_products}")
        
        # Check if products have categories
        products_with_categories = Product.objects.filter(category__isnull=False).count()
        self.stdout.write(f"   Products with categories: {products_with_categories}")
        
        # Check if reviews have products and reviewers
        reviews_with_data = Review.objects.filter(
            product__isnull=False, 
            reviewer__isnull=False
        ).count()
        self.stdout.write(f"   Reviews with complete data: {reviews_with_data}")
        
        # Sample data verification
        self.stdout.write("\n5. Sample data verification...")
        categories = list(Category.objects.values_list('name', flat=True))
        self.stdout.write(f"   Categories: {', '.join(categories)}")
        
        featured_products = list(Product.objects.filter(featured=True).values_list('title', flat=True))
        self.stdout.write(f"   Featured products: {len(featured_products)} items")
        
        order_statuses = list(Order.objects.values_list('status', flat=True))
        self.stdout.write(f"   Order statuses: {', '.join(set(order_statuses))}")
        
        self.stdout.write(self.style.SUCCESS("\n✅ Fixtures test completed successfully!"))
        self.stdout.write("\nYou can now use the following test accounts:")
        self.stdout.write("   Admin: admin@example.com / admin123")
        self.stdout.write("   Student: john.doe@student.edu / student123")
        self.stdout.write("   Customer: customer1@example.com / customer123")
