from django.test import TestCase
from django.contrib.auth.models import User
# from django.core.exceptions import ValidationError
from .models import Student, UserProfile  # Message, Reaction, Review, Cart, CartItem, CustomUser, WishList
from products.models import Product, Category


class MarketplaceModelsTest(TestCase):
    def setUp(self):
        """
        Set up a test user, a test category, and a test product.
        
        This method is called before each test in the class and is used
        to set up some common objects that can be used in the tests.
        
        A test user is created with the username 'testuser' and password
        '12345'. A test category is created with the name 'Test Category'.
        A test product is created with a title of 'Test Product', a description
        of 'Test Description', a price of 10.00, and is associated with the
        test category.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            title='Test Product',
            description='Test Description',
            price=10.00,
            category=self.category
        )

    def test_create_user_profile(self):
        """
        Test the creation of a UserProfile upon User creation.

        This test verifies that a UserProfile instance is automatically created
        when a new User is created. It checks that the UserProfile is associated
        with the correct User and that the default avatar is set correctly.
        """
        user = User.objects.create_user(username='testuser2', email='testuser2@example.com', password='testpass123')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual(user_profile.user, user)
        self.assertEqual(user_profile.avatar, 'avatars/default.jpg')
    
    # Test that UserProfile is also created
    def test_create_student_profile_on_user_creation(self):
        """
        Test the creation of a Student profile upon User creation.

        This test verifies that a Student instance is automatically created
        when a new User is created. It checks that the Student is associated
        with the correct User, that the email is set correctly, and that the
        string representation of the Student is correct.
        """
        new_user = User.objects.create_user(username='newuser', email='newuser@example.com', password='password123')
        self.assertTrue(Student.objects.filter(user=new_user).exists())
        student = Student.objects.get(user=new_user)
        self.assertEqual(student.email, 'newuser@example.com')
        self.assertEqual(str(student), f'{student.first_name} {student.last_name}')
    
        # Test that UserProfile is also created
        self.assertTrue(UserProfile.objects.filter(user=new_user).exists())

    def test_no_student_creation_for_existing_email(self):
        """
        Test that a Student instance is not created when a new User is created with
        an email that is already associated with a Student.

        This test verifies that when a new User is created with an email that is
        already associated with an existing Student, that Student is not
        associated with the new User. A new UserProfile is created as expected
        since the signal receiver does not check the email when creating a new
        UserProfile. The test also verifies that the existing Student is not
        deleted or modified in any way.
        """
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