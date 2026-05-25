import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from payment.models import Transaction
from payment import utils as payment_utils
from tests.factories import TransactionFactory, CustomUserFactory


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
            "/api/payment/transactions/verify_payment/",
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


