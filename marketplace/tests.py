from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from marketplace.models import Product, Cart, CartItem
from marketplace.views import add_to_cart
from django.test.client import RequestFactory


class AddToCartViewTest(TestCase):
    def setUp(self):
        """
        Setup a test user, a test product, and a test cart.
        Also log the test user in.
        """
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.product = Product.objects.create(title='Test Product', description='Test Description', price=10)
        self.cart = Cart.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_add_to_cart(self):
        """
        Test that a product can be added to the cart. This test checks that the add_to_cart view
        redirects to the cart page after adding the item to the cart, and that the item is added
        to the cart.
        """
        
        request = self.factory.post(reverse('marketplace:add_to_cart', kwargs={'product_id': self.product.id}), 
                                    data={'product_id': self.product.id, 'quantity': 1})
        request.user = self.user
        
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware()
        middleware.process_request(request)
        
        response = add_to_cart(request, product_id=self.product.id)
        self.assertEqual(response.status_code, 302)  # Redirect status code
        # Check if item is added to cart
        self.assertEqual(CartItem.objects.filter(cart=self.cart, product=self.product).count(), 1)
        self.assertRedirects(response, reverse('cart'))  # Check if the view redirects to cart page
        
    def test_invalid_form_submission(self):
        """
        Test that an invalid form submission does not add the item to the cart.
        The test simulates a POST request with no data, which is an invalid form submission.
        The test checks that the response is a redirect, that the item is not added to the cart, and that the view redirects to the home page.
        """
        request = self.factory.post(reverse('marketplace:add_to_cart', kwargs={'product_id': self.product.id}), data={})
        request.user = self.user
        
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware()
        middleware.process_request(request)
        
        response = add_to_cart(request, product_id=self.product.id)
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(CartItem.objects.filter(cart=self.cart, product=self.product).count(), 0)  # Check if item is not added to cart
        self.assertRedirects(response, reverse('home'))  # Check if the view redirects to home page when form is invalid
