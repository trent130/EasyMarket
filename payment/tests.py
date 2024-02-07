from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from payment.forms import PaymentForm
from .models import Transaction

User = get_user_model()

class PaymentAppViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.transaction = Transaction.objects.create(user=self.user, amount=10.00, description='Test transaction')

    def test_payment_list_view(self):
        response = self.client.get(reverse('payment_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/payment_list.html')


    def test_make_payment_form_valid(self):
        form = PaymentForm({
            'variant': 'default',
            'description': 'Payment description',
            'total': 1500.00,
            'currency': 'KES',
            'billing_first_name': 'John',
            'billing_last_name': 'Doe',
            'billing_address_1': '123 Main St',
            'billing_city': 'Anytown',
            'billing_postcode': '12345',
            'billing_country_code': 'Kenya',
        })
        self.assertTrue(form.is_valid())

    def test_make_payment_form_invalid(self):
        form = PaymentForm({})
        self.assertFalse(form.is_valid())
   
    def test_transaction_history_view(self):
        response = self.client.get(reverse('transaction_history'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/transaction_history.html')

    def test_transaction_detail_view(self):
        response = self.client.get(reverse('transaction_detail', args=[self.transaction.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/transaction_detail.html')

    def test_export_transactions_view(self):
        response = self.client.get(reverse('export_transactions'))
        self.assertEqual(response.status_code, 200)
        # Add more assertions based on your implementation

    def test_search_transactions_view(self):
        response = self.client.get(reverse('search_transactions'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'payment/search_transactions.html')