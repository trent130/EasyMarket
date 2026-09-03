import pytest
from decimal import Decimal
from unittest.mock import patch
from django.core.exceptions import ValidationError
from payment.models import Transaction
from payment import utils as payment_utils
from tests.factories import TransactionFactory, CustomUserFactory, OrderFactory


pytestmark = pytest.mark.django_db


def test_validate_phone_number_invalid_country():
    valid, _ = payment_utils.validate_phone_number("+15551234567")
    assert valid is False


def test_validate_phone_number_wrong_length():
    valid, _ = payment_utils.validate_phone_number("+25470000000")
    assert valid is False


def test_validate_payment_amount_invalid_method():
    valid, msg = payment_utils.validate_payment_amount(Decimal("100.00"), "BITCOIN")
    assert valid is False
    assert "Invalid" in msg


def test_format_currency_default():
    result = payment_utils.format_currency(Decimal("0"))
    assert "0.00" in result


def test_generate_transaction_id_contains_txn():
    txn_id = payment_utils.generate_transaction_id()
    assert "TXN" in txn_id


class TestTransactionModel:
    def test_str(self):
        txn = TransactionFactory()
        assert str(txn) == f"{txn.reference} - {txn.amount}"

    def test_pending_default(self):
        txn = TransactionFactory()
        assert txn.status == 'pending'

    def test_unique_transaction_id(self):
        TransactionFactory(transaction_id="UNIQUE001")
        with pytest.raises(Exception):
            TransactionFactory(transaction_id="UNIQUE001")

    def test_unique_reference(self):
        TransactionFactory(reference="REF001")
        with pytest.raises(Exception):
            TransactionFactory(reference="REF001")

    def test_unique_checkout_request_id(self):
        TransactionFactory(checkout_request_id="CR001")
        with pytest.raises(Exception):
            TransactionFactory(checkout_request_id="CR001")

    def test_negative_amount_rejected(self):
        user = CustomUserFactory()
        txn = TransactionFactory.build(amount=Decimal("-100.00"), user=user)
        with pytest.raises(ValidationError) as exc:
            txn.full_clean()
        assert 'amount' in exc.value.error_dict

    def test_zero_amount_rejected(self):
        user = CustomUserFactory()
        txn = TransactionFactory.build(amount=Decimal("0.00"), user=user)
        with pytest.raises(ValidationError) as exc:
            txn.full_clean()
        assert 'amount' in exc.value.error_dict


class TestPaymentUtils:
    def test_generate_transaction_id_format(self):
        txn_id = payment_utils.generate_transaction_id()
        assert txn_id.startswith("TXN")
        assert len(txn_id) > 10

    def test_validate_phone_number_valid(self):
        valid, cleaned = payment_utils.validate_phone_number("+254700000000")
        assert valid is True
        assert cleaned == "254700000000"

    def test_validate_phone_number_invalid(self):
        valid, _ = payment_utils.validate_phone_number("123")
        assert valid is False

    def test_validate_payment_amount_mpesa_valid(self):
        valid, _ = payment_utils.validate_payment_amount(Decimal("100.00"), "mpesa")
        assert valid is True

    def test_format_currency(self):
        result = payment_utils.format_currency(Decimal("1234.50"))
        assert "1,234.50" in result
        assert "KES" in result

    def test_calculate_transaction_fee_default(self):
        fee = payment_utils.calculate_transaction_fee(Decimal("1000.00"), "CASH")
        assert fee == Decimal("0.00")


class TestPaymentAPI:
    def test_list_requires_auth(self, client):
        resp = client.get("/api/payment/transactions/")
        assert resp.status_code == 401

    def test_list_authenticated(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/payment/transactions/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_history_requires_auth(self, client):
        resp = client.get("/api/payment/transactions/history/")
        assert resp.status_code == 401

    def test_history_authenticated(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/payment/transactions/history/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_receipt_requires_auth(self, client):
        resp = client.get("/api/payment/transactions/1/receipt/")
        assert resp.status_code == 401

    def test_verify_payment_validation(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/payment/verify/",
            {},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_refund_nonexistent_transaction(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/payment/transactions/99999/refund/",
            {"reason": "Defective"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 404

    def test_refund_uses_url_transaction_without_body_transaction_id(self, client):
        user = CustomUserFactory()
        transaction = TransactionFactory(user=user, status='completed')

        with patch('payment.views.MpesaClient') as mpesa_client:
            mpesa_client.return_value.process_refund.return_value = {
                'success': True,
                'refund_id': 'REFUND-1',
            }
            response = client.post(
                f'/api/payment/transactions/{transaction.transaction_id}/refund/',
                {'reason': 'Defective item'},
                content_type='application/json',
                **self._auth_headers(user),
            )

        assert response.status_code == 200
        assert response.data['refund_id'] == 'REFUND-1'
        transaction.refresh_from_db()
        assert transaction.status == 'refunded'

    def test_receipt_exposes_the_serializer_contract(self, client):
        user = CustomUserFactory()
        transaction = TransactionFactory(user=user, status='completed')

        response = client.get(
            f'/api/payment/transactions/{transaction.transaction_id}/receipt/',
            **self._auth_headers(user),
        )

        assert response.status_code == 200
        assert response.data['transaction_id'] == transaction.transaction_id
        assert response.data['status'] == 'completed'
        assert response.data['customer_name'] == user.full_name
        assert response.data['payment_method_details']['type'] == 'M-Pesa'

    def _auth_headers(self, user):
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_mpesa_initiation_rejects_another_users_order(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=CustomUserFactory(), payment_method='MPESA')

        with patch('payment.views.MpesaClient') as mpesa_client:
            response = client.post(
                '/api/payment/mpesa/',
                {'phone_number': '254700000000', 'order_id': order.id},
                content_type='application/json',
                **self._auth_headers(user),
            )

        assert response.status_code == 400
        mpesa_client.assert_not_called()

    def test_mpesa_initiation_returns_canonical_pending_response(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, payment_method='MPESA')

        with patch('payment.views.MpesaClient') as mpesa_client:
            mpesa_client.return_value.stk_push.return_value = {
                'ResponseCode': '0',
                'MerchantRequestID': 'MR-1',
                'CheckoutRequestID': 'CR-1',
            }
            response = client.post(
                '/api/payment/mpesa/',
                {'phone_number': '254700000000', 'order_id': order.id},
                content_type='application/json',
                **self._auth_headers(user),
            )

        assert response.status_code == 200
        assert set(response.data) == {
            'message', 'transaction_id', 'checkout_request_id', 'status'
        }
        assert response.data['message'] == 'Payment initiated'
        assert isinstance(response.data['transaction_id'], str)
        assert response.data['checkout_request_id'] == 'CR-1'
        assert response.data['status'] == 'pending'

    def test_payment_verification_rejects_another_users_transaction(self, client):
        owner = CustomUserFactory()
        attacker = CustomUserFactory()
        order = OrderFactory(user=owner, payment_method='MPESA')
        transaction = TransactionFactory(
            user=owner,
            amount=order.total_amount,
            reference=f'Order-{order.id}',
        )

        with patch('payment.views.MpesaClient') as mpesa_client:
            response = client.post(
                '/api/payment/verify/',
                {
                    'transaction_id': transaction.transaction_id,
                    'order_id': order.id,
                },
                content_type='application/json',
                **self._auth_headers(attacker),
            )

        assert response.status_code == 404
        mpesa_client.assert_not_called()

    def test_payment_verification_pending_is_lowercase(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, payment_method='MPESA')
        transaction = TransactionFactory(
            user=user,
            amount=order.total_amount,
            reference=f'Order-{order.id}',
        )

        with patch('payment.views.MpesaClient') as mpesa_client:
            mpesa_client.return_value.check_payment_status.return_value = 'PENDING'
            response = client.post(
                '/api/payment/verify/',
                {
                    'transaction_id': transaction.transaction_id,
                    'order_id': order.id,
                },
                content_type='application/json',
                **self._auth_headers(user),
            )

        assert response.status_code == 200
        assert response.data['status'] == 'pending'
        transaction.refresh_from_db()
        order.refresh_from_db()
        assert transaction.status == 'pending'
        assert order.payment_status is False

    def test_mpesa_callback_completes_transaction_and_order_for_string_result_code(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, payment_method='MPESA')
        transaction = TransactionFactory(
            user=user,
            amount=order.total_amount,
            reference=f'Order-{order.id}',
            checkout_request_id='CALLBACK-1',
        )

        response = client.post(
            '/api/payment/mpesa-callback/',
            {
                'Body': {
                    'stkCallback': {
                        'CheckoutRequestID': 'CALLBACK-1',
                        'ResultCode': '0',
                    }
                }
            },
            content_type='application/json',
        )

        assert response.status_code == 200
        transaction.refresh_from_db()
        order.refresh_from_db()
        assert transaction.status == 'completed'
        assert order.payment_status is True
        assert order.payment_date is not None

    def test_payment_verification_completion_updates_order_atomically(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, payment_method='MPESA')
        transaction = TransactionFactory(
            user=user,
            amount=order.total_amount,
            reference=f'Order-{order.id}',
        )

        with patch('payment.views.MpesaClient') as mpesa_client:
            mpesa_client.return_value.check_payment_status.return_value = 'COMPLETED'
            response = client.post(
                '/api/payment/verify/',
                {
                    'transaction_id': transaction.transaction_id,
                    'order_id': order.id,
                },
                content_type='application/json',
                **self._auth_headers(user),
            )

        assert response.status_code == 200
        assert response.data['status'] == 'completed'
        transaction.refresh_from_db()
        order.refresh_from_db()
        assert transaction.status == 'completed'
        assert order.payment_status is True
        assert order.payment_date is not None

    def test_transaction_financial_and_provider_fields_are_read_only(self, client):
        user = CustomUserFactory()
        transaction = TransactionFactory(user=user)
        original = {
            'amount': transaction.amount,
            'status': transaction.status,
            'payment_method': transaction.payment_method,
            'phone_number': transaction.phone_number,
            'reference': transaction.reference,
            'checkout_request_id': transaction.checkout_request_id,
            'description': transaction.description,
        }

        response = client.patch(
            f'/api/payment/transactions/{transaction.transaction_id}/',
            {
                'amount': '999.99',
                'status': 'completed',
                'payment_method': 'CASH',
                'phone_number': '254711111111',
                'reference': 'changed-reference',
                'checkout_request_id': 'changed-checkout',
                'description': 'changed-description',
            },
            content_type='application/json',
            **self._auth_headers(user),
        )

        assert response.status_code == 200
        transaction.refresh_from_db()
        for field, value in original.items():
            assert getattr(transaction, field) == value
