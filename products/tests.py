from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Product, Category, Image

class ProductViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.category = Category.objects.create(name='Test Category')
        self.user_id = 1
        self.product = Product.objects.create(title='Test Product', description='Test Description', price=10.00, category=self.category)
        self.image = Image.objects.create(product=self.product, image='test_image.jpg', description='Test Image')

    def test_product_view(self):
        response = self.client.get(reverse('products:product', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product.html')
        self.assertContains(response, self.product.title)
        self.assertContains(response, self.product.description)
        self.assertContains(response, self.image.image.url)

    def test_product_list_view(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_list.html')
        self.assertIn(self.product, response.context['page_obj'])

    def test_product_detail_view(self):
        response = self.client.get(reverse('products:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product_detail.html')
        self.assertEqual(self.product, response.context['product'])

    def test_add_product_view(self):
        response = self.client.get(reverse('products:add_product'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/add_product.html')

        # Test form submission
        form_data = {
            'title': 'New Product',
            'description': 'New Description',
            'price': 20.00,
            'category': self.category.id,
            # Include form data for image upload if applicable
        }
        response = self.client.post(reverse('products:add_product'), form_data)
        print(response.status_code)
        print(response.content)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful form submission
        self.assertTrue(Product.objects.filter(title='New Product').exists())

    def test_user_product_list_view(self):
        response = self.client.get(reverse('products:user_product_list', kwargs={'user_id': self.user_id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'products/product.html')
        self.assertIn(self.product, response.context['products'])

    def test_category_view(self):
        response = self.client.get(reverse('products:categories'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'staticpages/categories.html')
        self.assertIn(self.category, response.context['categories'])
