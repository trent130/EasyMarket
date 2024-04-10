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
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.product = Product.objects.create(title='Test Product', description='Test Description', price=10)
        self.cart = Cart.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpassword')
        
    def test_add_to_cart(self):
        request = self.factory.post(reverse('marketplace:add_to_cart', kwargs={'product_id': self.product.id}), data={'product_id': self.product.id, 'quantity': 1})
        request.user = self.user
        
        middleware = SessionMiddleware()
        middleware.process_request(request)
        request.session.save()
        
        middleware = MessageMiddleware()
        middleware.process_request(request)
        
        response = add_to_cart(request, product_id=self.product.id)
        self.assertEqual(response.status_code, 302)  # Redirect status code
        self.assertEqual(CartItem.objects.filter(cart=self.cart, product=self.product).count(), 1)  # Check if item is added to cart
        self.assertRedirects(response, reverse('cart'))  # Check if the view redirects to cart page
        
    def test_invalid_form_submission(self):
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
