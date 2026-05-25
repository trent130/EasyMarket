import factory
from django.conf import settings
from users.models import CustomUser, Student, UserProfile
from products.models import Product, Category, ProductVariant
from orders.models import Order, OrderItem, ShippingAddress, Refund
from payment.models import Transaction
from marketplace.models import Message, Reaction, Review, Cart, CartItem, WishList


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    first_name = "Test"
    last_name = "User"
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    user_type = 'customer'
    is_active = True


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    user = factory.SubFactory(CustomUserFactory)
    bio = "Test bio"
    phone_number = "+254700000000"
    university = "Test University"
    student_id = factory.Sequence(lambda n: f"STU{n:05d}")


class UserProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory(CustomUserFactory)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Category {n}")
    description = "Test category description"


class ProductVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductVariant

    name = "Default"
    sku = factory.Sequence(lambda n: f"SKU{n:05d}")
    stock = 10
    price_adjustment = 0


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    title = factory.Sequence(lambda n: f"Product {n}")
    description = "Test product description"
    price = 100.00
    student = factory.SubFactory(StudentFactory)
    category = factory.SubFactory(CategoryFactory)
    stock = 10
    condition = 'new'


class ShippingAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ShippingAddress

    user = factory.SubFactory(CustomUserFactory)
    first_name = "Test"
    last_name = "User"
    email = factory.Sequence(lambda n: f"addr{n}@example.com")
    phone = "+254700000000"
    address = "123 Test Street"
    city = "Nairobi"
    postal_code = "00100"


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(CustomUserFactory)
    reference = factory.Sequence(lambda n: f"ORD{n:06d}")
    total_amount = 100.00
    status = 'pending'
    payment_method = 'CASH'


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1
    price = 100.00


class RefundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Refund

    order = factory.SubFactory(OrderFactory)
    reason = "Defective item"


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    transaction_id = factory.Sequence(lambda n: f"TXN{n:015d}")
    merchant_request_id = factory.Sequence(lambda n: f"MR{n:010d}")
    payment_method = 'MPESA'
    user = factory.SubFactory(CustomUserFactory)
    amount = 100.00
    phone_number = "+254700000000"
    reference = factory.Sequence(lambda n: f"REF{n:08d}")
    description = "Test payment"
    checkout_request_id = factory.Sequence(lambda n: f"CR{n:015d}")
    status = 'pending'


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    user = factory.SubFactory(CustomUserFactory)
    content = "Test message content"


class ReactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reaction

    reaction_type = 'like'
    user = factory.SubFactory(CustomUserFactory)
    message_sent = factory.SubFactory(MessageFactory)


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    product = factory.SubFactory(ProductFactory)
    reviewer = factory.SubFactory(CustomUserFactory)
    rating = 4
    comment = "Great product"


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(CustomUserFactory)
    slug = factory.Sequence(lambda n: f"cart-{n}")


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = 1


class WishListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WishList

    user = factory.SubFactory(CustomUserFactory)
