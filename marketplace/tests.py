import pytest
from decimal import Decimal
from django.db import IntegrityError
from marketplace.models import Message, Reaction, Review, Cart, CartItem, WishList
from tests.factories import (
    MessageFactory, ReactionFactory, ReviewFactory,
    CartFactory, CartItemFactory, ProductFactory, CustomUserFactory,
    CategoryFactory
)


pytestmark = pytest.mark.django_db


class TestMessage:
    def test_str(self):
        msg = MessageFactory()
        assert msg.user.username in str(msg)

    def test_default_unread(self):
        msg = MessageFactory()
        assert msg.read is False

    def test_mark_as_read(self):
        msg = MessageFactory()
        msg.read = True
        msg.save()
        assert msg.read is True


class TestReaction:
    def test_str(self):
        reaction = ReactionFactory(reaction_type='like')
        assert "like" in str(reaction)


class TestReview:
    def test_str(self):
        review = ReviewFactory(rating=4)
        assert str(review) == f"Review for {review.product.title} by {review.reviewer.username}"

    def test_unique_reviewer_per_product(self):
        product = ProductFactory()
        reviewer = CustomUserFactory()
        ReviewFactory(product=product, reviewer=reviewer)
        with pytest.raises(IntegrityError):
            ReviewFactory(product=product, reviewer=reviewer)

    def test_different_reviewer_allowed(self):
        product = ProductFactory()
        r1 = CustomUserFactory()
        r2 = CustomUserFactory()
        ReviewFactory(product=product, reviewer=r1)
        ReviewFactory(product=product, reviewer=r2)

    def test_rating_below_min_rejected(self):
        review = ReviewFactory.build(rating=0)
        with pytest.raises(Exception):
            review.full_clean()

    def test_rating_above_max_rejected(self):
        review = ReviewFactory.build(rating=6)
        with pytest.raises(Exception):
            review.full_clean()


class TestCart:
    def test_total_items_empty(self):
        cart = CartFactory()
        assert cart.total_items() == 0

    def test_total_items_with_products(self):
        cart = CartFactory()
        CartItemFactory(cart=cart, quantity=2)
        CartItemFactory(cart=cart, quantity=3)
        assert cart.total_items() == 5

    def test_total_price_empty(self):
        cart = CartFactory()
        assert cart.total_price() == Decimal("0.00")

    def test_total_price_with_items(self):
        cart = CartFactory()
        p1 = ProductFactory(price=Decimal("50.00"))
        p2 = ProductFactory(price=Decimal("100.00"))
        CartItemFactory(cart=cart, product=p1, quantity=2)
        CartItemFactory(cart=cart, product=p2, quantity=1)
        assert cart.total_price() == Decimal("200.00")

    def test_slug_generated(self):
        cart = CartFactory()
        assert cart.slug is not None
        assert len(cart.slug) > 0


class TestCartItem:
    def test_total_price(self):
        product = ProductFactory(price=Decimal("25.00"))
        item = CartItemFactory(product=product, quantity=3)
        assert item.total_price() == Decimal("75.00")

    def test_total_price_single(self):
        product = ProductFactory(price=Decimal("99.99"))
        item = CartItemFactory(product=product, quantity=1)
        assert item.total_price() == Decimal("99.99")


class TestWishList:
    def test_auto_created_on_user_create(self):
        user = CustomUserFactory()
        assert WishList.objects.filter(user=user).exists()

    def test_str(self):
        user = CustomUserFactory()
        wishlist = WishList.objects.get(user=user)
        assert str(wishlist) == f"{user.username}'s wishlist"


class TestCartAPI:
    def test_add_to_cart(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/cart/add/",
            {"product_id": product.id, "quantity": 2},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["action"] == "created"

    def test_add_to_cart_no_auth(self, client):
        resp = client.post("/api/marketplace/cart/add/", {"product_id": 1})
        assert resp.status_code == 401

    def test_add_to_cart_missing_product_id(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/cart/add/", {},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400
        assert "product_id" in resp.json()["error"]

    def test_add_to_cart_invalid_quantity(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/cart/add/",
            {"product_id": product.id, "quantity": -1},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_add_to_cart_insufficient_stock(self, client):
        user = CustomUserFactory()
        product = ProductFactory(stock=1)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/cart/add/",
            {"product_id": product.id, "quantity": 999},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_cart_list(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=3)
        resp = client.get(
            "/api/marketplace/cart/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_cart_remove_item(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        item = CartItemFactory(cart=cart, product=product, quantity=1)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/marketplace/cart/{cart.id}/remove_item/",
            {"item_id": item.id},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204

    def test_cart_clear(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=2)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/marketplace/cart/{cart.id}/clear/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204

    def test_cart_update_quantity(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product, quantity=1)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/cart/update_quantity/",
            {"product_id": product.id, "quantity": 5},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200


class TestWishListAPI:
    def test_wishlist_list_creates_on_first_access(self, client):
        user = CustomUserFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/marketplace/wishlist/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_wishlist_add_product(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/wishlist/add/",
            {"product_id": product.id},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 201

    def test_wishlist_add_product_no_auth(self, client):
        resp = client.post("/api/marketplace/wishlist/add/", {"product_id": 1})
        assert resp.status_code == 401

    def test_wishlist_remove_product(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        wishlist = WishList.objects.get(user=user)
        wishlist.products.add(product)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/wishlist/remove/",
            {"product_id": product.id},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204

    def test_wishlist_add_by_slug(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/marketplace/wishlist/{product.slug}/add/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200


class TestSearchAPI:
    def test_search_requires_auth(self, client):
        resp = client.get("/api/marketplace/search/", {"q": "test"})
        assert resp.status_code == 401

    def test_search_with_auth(self, client):
        user = CustomUserFactory()
        ProductFactory(title="Searchable Textbook")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/marketplace/search/",
            {"q": "Searchable"},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_search_with_filters(self, client):
        user = CustomUserFactory()
        cat = CategoryFactory()
        ProductFactory(title="Filtered Item", price="15.00", category=cat)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/marketplace/search/",
            {"q": "Filtered", "category": cat.id, "min_price": "10", "max_price": "20", "sort_by": "price_asc"},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_recommendations_requires_auth(self, client):
        resp = client.get("/api/marketplace/recommendations/")
        assert resp.status_code == 401

    def test_recommendations_authenticated(self, client):
        user = CustomUserFactory()
        cat = CategoryFactory()
        product = ProductFactory(category=cat)
        cart = CartFactory(user=user)
        CartItemFactory(cart=cart, product=product)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/marketplace/recommendations/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_wishlist_check_product(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            f"/api/marketplace/wishlist/{product.slug}/check/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_wishlist_by_seller(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        wishlist = WishList.objects.get(user=user)
        wishlist.products.add(product)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/marketplace/wishlist/by-seller/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200


class TestReviewAPI:
    def test_create_review_requires_auth(self, client):
        resp = client.post("/api/marketplace/reviews/", {"rating": 5})
        assert resp.status_code == 401

    def test_create_review(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            "/api/marketplace/reviews/",
            {"product": product.id, "rating": 5, "comment": "Great!"},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 201

    def test_list_reviews(self, client):
        user = CustomUserFactory()
        ReviewFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            "/api/marketplace/reviews/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_update_review(self, client):
        user = CustomUserFactory()
        review = ReviewFactory(reviewer=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.patch(
            f"/api/marketplace/reviews/{review.pk}/",
            {"comment": "Updated review"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_delete_review(self, client):
        user = CustomUserFactory()
        review = ReviewFactory(reviewer=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.delete(
            f"/api/marketplace/reviews/{review.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204


class TestWishlistCRUD:
    def test_wishlist_retrieve(self, client):
        user = CustomUserFactory()
        wishlist = WishList.objects.get(user=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.get(
            f"/api/marketplace/wishlist/{wishlist.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_wishlist_update(self, client):
        user = CustomUserFactory()
        wishlist = WishList.objects.get(user=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.patch(
            f"/api/marketplace/wishlist/{wishlist.pk}/",
            {"name": "Updated Wishlist"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_wishlist_destroy(self, client):
        user = CustomUserFactory()
        wishlist = WishList.objects.get(user=user)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.delete(
            f"/api/marketplace/wishlist/{wishlist.pk}/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204


class TestWishlistAddRemoveBySlug:
    def test_add_product_by_slug_success(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/marketplace/wishlist/{product.slug}/add/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code in (200, 201)

    def test_remove_product_by_slug_success(self, client):
        user = CustomUserFactory()
        product = ProductFactory()
        wishlist = WishList.objects.get(user=user)
        wishlist.products.add(product)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(user)
        resp = client.post(
            f"/api/marketplace/wishlist/{product.slug}/remove/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204
