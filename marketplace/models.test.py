from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, UserProfile, Message, Reaction, Review, Cart, CartItem, CustomUser, WishList
from products.models import Product, Category

class MarketplaceModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            title='Test Product',
            description='Test Description',
            price=10.00,
            category=self.category
        )
def test_create_user_profile(self):
    user = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass123')
    self.assertTrue(UserProfile.objects.filter(user=user).exists())
    user_profile = UserProfile.objects.get(user=user)
    self.assertEqual(user_profile.user, user)
    self.assertEqual(user_profile.avatar, 'avatars/default.jpg')def test_create_student_profile_on_user_creation(self):
        new_user = User.objects.create_user(username='newuser', email='newuser@example.com', password='password123')
    self.assertTrue(Student.objects.filter(user=new_user).exists())
        student = Student.objects.get(user=new_user)
        self.assertEqual(student.email, 'newuser@example.com')
        self.assertEqual(str(student), f'{student.first_name} {student.last_name}')
    
        # Test that UserProfile is also created
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())def test_no_student_creation_for_existing_email(self):
            existing_email = 'existing@example.com'
            Student.objects.create(
                user=self.user,
                first_name='Existing',
                last_name='Student',
                email=existing_email
            )
        
            new_user = User.objects.create_user(
                username='newuser',
                email=existing_email,
                password='password123'
            )
        
            self.assertTrue(UserProfile.objects.filter(user=new_user).exists())
            self.assertEqual(Student.objects.filter(email=existing_email).count(), 1)
            self.assertFalse(Student.objects.filter(user=new_user).exists())