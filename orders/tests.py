import pytest
from decimal import Decimal
from orders.models import Order, Refund
from tests.factories import OrderFactory, OrderItemFactory, ShippingAddressFactory, CustomUserFactory, ProductFactory


pytestmark = pytest.mark.django_db


class TestOrderModel:
    def test_is_paid_true(self):
        order = OrderFactory(payment_status=True)
        assert order.is_paid is True

    def test_is_paid_false(self):
        order = OrderFactory(payment_status=False)
        assert order.is_paid is False

    def test_str(self):
        order = OrderFactory()
        assert str(order) == f"Order #{order.id} - {order.user.username}"

    def test_negative_total_rejected(self):
        order = OrderFactory.build(total_amount=Decimal("-50.00"))
        with pytest.raises(Exception):
            order.full_clean()

    def test_can_request_refund_delivered_and_paid(self):
        order = OrderFactory(status='delivered', payment_status=True)
        assert order.can_request_refund is True

    def test_cannot_request_refund_unpaid(self):
        order = OrderFactory(status='delivered', payment_status=False)
        assert order.can_request_refund is False

    def test_cannot_request_refund_wrong_status(self):
        order = OrderFactory(status='pending', payment_status=True)
        assert order.can_request_refund is False

    def test_cannot_request_refund_canceled(self):
        order = OrderFactory(status='canceled', payment_status=True)
        assert order.can_request_refund is False

    def test_create_refund_request(self):
        order = OrderFactory(status='delivered', payment_status=True)
        refund = order.create_refund_request(reason="Defective item")
        assert refund.order == order
        assert refund.reason == "Defective item"
        assert refund.status == 'pending'

    def test_generate_invoice_returns_bytes(self):
        order = OrderFactory()
        OrderItemFactory(order=order, quantity=2, price=Decimal("50.00"))
        invoice = order.generate_invoice()
        assert isinstance(invoice, bytes)
        assert len(invoice) > 0

    def test_generate_invoice_with_order_items(self):
        order = OrderFactory(total_amount=Decimal("150.00"))
        OrderItemFactory(order=order, quantity=1, price=Decimal("100.00"))
        OrderItemFactory(order=order, quantity=1, price=Decimal("50.00"))
        invoice = order.generate_invoice()
        assert isinstance(invoice, bytes)


class TestShippingAddress:
    def test_default_shipping_address(self):
        addr = ShippingAddressFactory(is_default=True)
        assert addr.is_default is True


class TestOrderItem:
    def test_order_item_creation(self):
        item = OrderItemFactory(quantity=2)
        assert item.quantity == 2
        assert item.price > 0


class TestRefund:
    def test_default_status(self):
        order = OrderFactory()
        refund = Refund.objects.create(order=order, reason="Damaged")
        assert refund.status == 'pending'


class TestOrderAPI:
    def test_order_list_requires_auth(self, client):
        resp = client.get("/api/orders/orders/")
        assert resp.status_code == 401

    def test_order_list_authenticated(self, client):
        user = CustomUserFactory()
        OrderFactory(user=user)
        OrderFactory(user=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/orders/orders/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200
        assert resp.json()["count"] >= 2

    def test_track_order(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            f"/api/orders/orders/{order.id}/track/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_create_order(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/orders/orders/",
            {
                "items": [{"product_id": product.id, "quantity": 1}],
                "payment_method": "CASH"
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        if resp.status_code != 201:
            print("CREATE ORDER ERROR:", resp.content.decode()[:1000])
        assert resp.status_code == 201

    def test_cancel_order(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, status="pending")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/orders/orders/{order.id}/cancel/",
            {"reason": "Changed my mind"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_cancel_shipped_order(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, status="shipped")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/orders/orders/{order.id}/cancel/",
            {"reason": "Too late"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_create_order_invalid_product(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/orders/orders/",
            {
                "items": [{"product_id": 99999, "quantity": 1}],
                "payment_method": "CASH"
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_order_detail(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            f"/api/orders/orders/{order.id}/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_confirm_delivery_shipped(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, status="shipped")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/orders/orders/{order.id}/confirm_delivery/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_confirm_delivery_not_shipped(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, status="pending")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/orders/orders/{order.id}/confirm_delivery/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_update_order(self, client):
        user = CustomUserFactory()
        order = OrderFactory(user=user, status="pending")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.patch(
            f"/api/orders/orders/{order.id}/",
            {"status": "processing"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200
