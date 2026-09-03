import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from products.models import Product, Category, ProductVariant
from products.serializers import ProductVariantSerializer
from tests.factories import (
    ProductFactory, CategoryFactory, ProductVariantFactory, StudentFactory,
    ReviewFactory
)


pytestmark = pytest.mark.django_db


class TestCategory:
    def test_slug_auto_generated(self):
        cat = CategoryFactory(name="My Category")
        assert cat.slug == "my-category"

    def test_str(self):
        cat = CategoryFactory(name="Books")
        assert str(cat) == "Books"

    def test_active_products_count(self):
        cat = CategoryFactory()
        ProductFactory(category=cat, is_active=True)
        ProductFactory(category=cat, is_active=True)
        ProductFactory(category=cat, is_active=False)
        assert cat.active_products_count == 2


class TestProductValidation:
    def test_negative_price_rejected(self):
        student = StudentFactory()
        category = CategoryFactory()
        p = ProductFactory.build(price=Decimal("-10.00"), student=student, category=category)
        with pytest.raises(ValidationError) as exc:
            p.full_clean()
        assert 'price' in exc.value.error_dict

    def test_min_price_allowed(self):
        student = StudentFactory()
        category = CategoryFactory()
        p = ProductFactory.build(price=Decimal("0.01"), student=student, category=category)
        p.full_clean()

    def test_negative_stock_rejected(self):
        student = StudentFactory()
        category = CategoryFactory()
        p = ProductFactory.build(stock=-1, student=student, category=category)
        with pytest.raises(ValidationError) as exc:
            p.full_clean()
        assert 'stock' in exc.value.error_dict

    def test_reserved_exceeds_stock_rejected(self):
        student = StudentFactory()
        category = CategoryFactory()
        p = ProductFactory.build(stock=5, reserved_stock=10, student=student, category=category)
        with pytest.raises(ValidationError) as exc:
            p.full_clean()
        assert 'reserved_stock' in exc.value.error_dict


class TestProductSlug:
    def test_slug_generated_on_save(self):
        p = ProductFactory(title="Calculus 101")
        assert p.slug.startswith("calculus-101")

    def test_unique_slugs(self):
        p1 = ProductFactory(title="Same Title")
        p2 = ProductFactory(title="Same Title")
        assert p1.slug != p2.slug


class TestProductStock:
    def test_available_stock(self):
        p = ProductFactory(stock=10, reserved_stock=3)
        assert p.available_stock == 7

    def test_available_stock_no_reservation(self):
        p = ProductFactory(stock=10, reserved_stock=0)
        assert p.available_stock == 10

    def test_available_stock_floor_at_zero(self):
        p = ProductFactory(stock=5)
        Product.objects.filter(pk=p.pk).update(stock=2, reserved_stock=5)
        p.refresh_from_db()
        assert p.available_stock == 0

    def test_is_in_stock_true(self):
        p = ProductFactory(stock=10, reserved_stock=3)
        assert p.is_in_stock() is True

    def test_is_in_stock_false_when_exhausted(self):
        p = ProductFactory(stock=5, reserved_stock=5)
        assert p.is_in_stock() is False

    def test_reserve_stock_reduces_available(self):
        p = ProductFactory(stock=10)
        p.reserve_stock(3)
        p.refresh_from_db()
        assert p.reserved_stock == 3

    def test_reserve_stock_insufficient_raises(self):
        p = ProductFactory(stock=2)
        with pytest.raises(ValidationError, match="Not enough stock"):
            p.reserve_stock(5)

    def test_release_stock(self):
        p = ProductFactory(stock=10, reserved_stock=5)
        p.release_stock(3)
        p.refresh_from_db()
        assert p.reserved_stock == 2

    def test_default_category(self):
        student = StudentFactory()
        product = Product.objects.create(
            title="Default Cat Test",
            description="Desc",
            price=Decimal("10.00"),
            student=student,
            condition="new",
            stock=5,
        )
        assert product.category is not None
        assert product.category.name == "Uncategorized"

    def test_update_stock_changes_total(self):
        p = ProductFactory(stock=5)
        p.update_stock(20)
        p.refresh_from_db()
        assert p.stock == 20

    def test_update_stock_negative_reserved_rejected(self):
        p = ProductFactory(stock=5, reserved_stock=5)
        with pytest.raises(ValidationError, match="reserved stock"):
            p.update_stock(2)


class TestProductVariant:
    def test_price_with_product(self):
        variant = ProductVariantFactory(price_adjustment="5.00")
        product = ProductFactory()
        product.variants.add(variant)
        serializer = ProductVariantSerializer(variant)
        data = serializer.data
        assert "final_price" in data

    def test_str(self):
        v = ProductVariantFactory(name="Large", sku="LARGE001")
        assert str(v) == "Large - LARGE001"

    def test_unique_sku(self):
        ProductVariantFactory(sku="DUPESKU")
        with pytest.raises(Exception):
            ProductVariantFactory(sku="DUPESKU")


class TestProductProperties:
    def test_increment_views(self):
        p = ProductFactory(views_count=0)
        p.increment_views()
        p.refresh_from_db()
        assert p.views_count == 1

    def test_average_rating_no_reviews(self):
        p = ProductFactory()
        assert p.average_rating == 0

    def test_review_count_no_reviews(self):
        p = ProductFactory()
        assert p.review_count == 0


class TestProductAPI:
    def test_category_list(self, client):
        CategoryFactory(name="Books")
        CategoryFactory(name="Electronics")
        resp = client.get("/api/products/categories/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 2

    def test_product_list(self, client):
        ProductFactory(title="Product A")
        ProductFactory(title="Product B")
        resp = client.get("/api/products/products/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] >= 2

    def test_product_list_excludes_inactive_and_drafts(self, client):
        ProductFactory(title="Visible", is_active=True, is_draft=False)
        ProductFactory(title="Inactive", is_active=False, is_draft=False)
        ProductFactory(title="Draft", is_active=True, is_draft=True)

        resp = client.get("/api/products/products/")

        assert resp.status_code == 200
        titles = {product["title"] for product in resp.json()["results"]}
        assert titles == {"Visible"}

    def test_product_detail_by_slug(self, client):
        p = ProductFactory(title="Unique Detail")
        resp = client.get(f"/api/products/products/slug/{p.slug}/")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Unique Detail"

    def test_featured_products(self, client):
        ProductFactory(featured=True)
        ProductFactory(featured=True)
        resp = client.get("/api/products/products/featured/")
        assert resp.status_code == 200
        assert len(resp.json()) >= 2

    def test_trending_products(self, client):
        ProductFactory()
        resp = client.get("/api/products/products/trending/")
        assert resp.status_code == 200

    def test_conditions_endpoint(self, client):
        resp = client.get("/api/products/products/conditions/")
        assert resp.status_code == 200

    def test_search_endpoint(self, client):
        ProductFactory(title="Searchable Item")
        resp = client.get("/api/products/products/search/", {"q": "Searchable"})
        assert resp.status_code == 200

    def test_my_products_requires_auth(self, client):
        resp = client.get("/api/products/products/my-products/")
        assert resp.status_code == 401

    def test_product_detail_by_id(self, client):
        p = ProductFactory(title="Detail by ID")
        resp = client.get(f"/api/products/products/{p.id}/")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Detail by ID"

    def test_product_detail_by_slug_lookup(self, client):
        p = ProductFactory(title="Detail by Slug")
        resp = client.get(f"/api/products/products/{p.slug}/")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Detail by Slug"

    def test_create_product_requires_auth(self, client):
        resp = client.post("/api/products/products/", {"title": "Test"})
        assert resp.status_code == 401

    def test_create_product_authenticated(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        category = CategoryFactory()
        resp = client.post(
            "/api/products/products/",
            {
                "title": "New Product", "description": "Desc",
                "price": "19.99", "category": category.id,
                "condition": "new", "stock": 10
            },
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 201

    def test_my_products_authenticated(self, client):
        student = StudentFactory()
        ProductFactory(student=student)
        product2 = ProductFactory(student=student)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.get(
            f"/api/products/products/my-products/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200
        assert resp.json()["count"] >= 2
        assert resp.json()["count"] >= 1

    def test_create_product_invalid_price(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        category = CategoryFactory()
        resp = client.post(
            "/api/products/products/",
            {
                "title": "Bad", "description": "Desc",
                "price": "-5.00", "category": category.id,
                "condition": "new", "stock": 10
            },
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_update_product(self, client):
        student = StudentFactory()
        product = ProductFactory(student=student, title="Original")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.patch(
            f"/api/products/products/{product.slug}/",
            {"title": "Updated Title", "price": "29.99"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_update_product_rejects_a_different_owner(self, client):
        owner = StudentFactory()
        other_student = StudentFactory()
        product = ProductFactory(student=owner, title="Original")
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(other_student.user)

        resp = client.patch(
            f"/api/products/products/{product.slug}/",
            {"title": "Should not change", "price": "29.99"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert resp.status_code == 404
        product.refresh_from_db()
        assert product.title == "Original"

    def test_delete_product_image_requires_ownership(self, client):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.core.files.storage import default_storage
        from rest_framework_simplejwt.tokens import AccessToken

        owner = StudentFactory()
        other_student = StudentFactory()
        product = ProductFactory(student=owner)
        product.image = SimpleUploadedFile(
            "owned-image.jpg",
            b"not-a-real-image",
            content_type="image/jpeg",
        )
        product.save()
        image_path = product.image.name

        token = AccessToken.for_user(other_student.user)
        response = client.delete(
            "/api/products/products/my-products/delete-image/",
            {"image_url": f"/media/{image_path}"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        assert response.status_code == 404
        assert default_storage.exists(image_path)
        product.image.delete(save=False)

    def test_delete_product(self, client):
        student = StudentFactory()
        product = ProductFactory(student=student)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.delete(
            f"/api/products/products/{product.slug}/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204

    def test_update_product_requires_auth(self, client):
        product = ProductFactory()
        resp = client.patch(f"/api/products/products/{product.slug}/", {"title": "Hack"})
        assert resp.status_code == 401

    def test_delete_product_requires_auth(self, client):
        product = ProductFactory()
        resp = client.delete(f"/api/products/products/{product.slug}/")
        assert resp.status_code == 401

    def test_bulk_action_requires_auth(self, client):
        resp = client.post("/api/products/products/bulk_action/", {})
        assert resp.status_code == 401

    def test_update_stock_requires_auth(self, client):
        resp = client.post("/api/products/products/1/update_stock/", {})
        assert resp.status_code == 401

    def test_validate_product(self, client):
        student = StudentFactory()
        cat = CategoryFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/products/products/validate_product/",
            {"title": "Valid", "description": "Desc", "price": "10.00", "category": cat.id, "condition": "new", "stock": 5},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_update_stock_authenticated(self, client):
        student = StudentFactory()
        product = ProductFactory(student=student, stock=10)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            f"/api/products/products/{product.slug}/update_stock/",
            {"stock": 5},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_bulk_action_authenticated(self, client):
        student = StudentFactory()
        p1 = ProductFactory(student=student)
        p2 = ProductFactory(student=student)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/products/products/bulk-action/",
            {"product_ids": [p1.id, p2.id], "action": "deactivate"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204

    def test_save_draft(self, client):
        student = StudentFactory()
        cat = CategoryFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/products/products/my-products/draft/",
            {"title": "Draft Product", "description": "Draft desc", "category": cat.id, "price": "15.00", "condition": "new"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 201

    def test_manage_draft_get(self, client):
        student = StudentFactory()
        product = ProductFactory(student=student, is_active=False, is_draft=True)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.get(
            f"/api/products/products/my-products/draft/{product.id}/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_publish_draft(self, client):
        student = StudentFactory()
        product = ProductFactory(student=student, is_active=False, is_draft=True)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            f"/api/products/products/my-products/draft/{product.id}/publish/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_manage_draft_patch(self, client):
        student = StudentFactory()
        product = ProductFactory(student=student, is_active=False, is_draft=True)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.patch(
            f"/api/products/products/my-products/draft/{product.id}/",
            {"title": "Updated Draft", "price": "25.00"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_manage_draft_delete(self, client):
        student = StudentFactory()
        product = ProductFactory(student=student, is_active=False, is_draft=True)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.delete(
            f"/api/products/products/my-products/draft/{product.id}/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 204

    def test_retrieve_by_slug(self, client):
        product = ProductFactory()
        resp = client.get(f"/api/products/products/slug/{product.slug}/")
        assert resp.status_code == 200

    def test_search_public(self, client):
        ProductFactory(title="Searchable Book")
        resp = client.get("/api/products/products/search/", {"q": "Searchable"})
        assert resp.status_code == 200

    def test_trending(self, client):
        ProductFactory()
        resp = client.get("/api/products/products/trending/")
        assert resp.status_code == 200

    def test_conditions(self, client):
        resp = client.get("/api/products/products/conditions/")
        assert resp.status_code == 200

    def test_featured(self, client):
        ProductFactory(is_active=True)
        resp = client.get("/api/products/products/featured/")
        assert resp.status_code == 200

    def test_my_products_list_authenticated(self, client):
        student = StudentFactory()
        ProductFactory(student=student)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.get(
            "/api/products/products/my-products/",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 200

    def test_category_products(self, client):
        cat = CategoryFactory()
        ProductFactory(category=cat, is_active=True)
        resp = client.get(f"/api/products/categories/{cat.slug}/products/")
        assert resp.status_code == 200
        cat = CategoryFactory()
        ProductFactory(category=cat, is_active=True)
        resp = client.get(f"/api/products/categories/{cat.slug}/products/")
        assert resp.status_code == 200

    def test_category_detail_by_slug(self, client):
        from django.core.cache import cache

        category = CategoryFactory()
        cache.clear()

        response = client.get(f"/api/products/categories/{category.slug}/")

        assert response.status_code == 200
        assert response.json()["slug"] == category.slug

    def test_category_list_excludes_inactive_categories(self, client):
        from django.core.cache import cache

        CategoryFactory(name="Visible category", is_active=True)
        CategoryFactory(name="Hidden category", is_active=False)
        cache.clear()

        response = client.get("/api/products/categories/")

        assert response.status_code == 200
        names = {item["name"] for item in response.json()["results"]}
        assert "Visible category" in names
        assert "Hidden category" not in names

    def test_category_stats(self, client):
        category = CategoryFactory()
        ProductFactory(category=category, is_active=True)

        response = client.get("/api/products/categories/stats/")

        assert response.status_code == 200
        result = next(item for item in response.json()["categories"] if item["id"] == category.id)
        assert result["product_count"] == 1

    def test_upload_image_no_image(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.post(
            "/api/products/products/my-products/upload-image/",
            {},
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_upload_image_requires_auth(self, client):
        resp = client.post(
            "/api/products/products/my-products/upload-image/",
            {},
        )
        assert resp.status_code == 401

    def test_delete_image_missing_url(self, client):
        student = StudentFactory()
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(student.user)
        resp = client.delete(
            "/api/products/products/my-products/delete-image/",
            {},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_product_detail_not_found(self, client):
        resp = client.get("/api/products/products/nonexistent-slug/")
        assert resp.status_code == 404

    def test_product_update_wrong_user(self, client):
        student = StudentFactory()
        other = StudentFactory()
        product = ProductFactory(student=student)
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken.for_user(other.user)
        resp = client.patch(
            f"/api/products/products/{product.slug}/",
            {"title": "Hacked"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        assert resp.status_code == 400

    def test_product_with_variants_detail(self, client):
        variant = ProductVariantFactory()
        product = ProductFactory()
        product.variants.add(variant)
        resp = client.get(f"/api/products/products/{product.slug}/")
        assert resp.status_code == 200

    def test_increment_views_model(self):
        product = ProductFactory()
        product.increment_views()
        product.refresh_from_db()
        assert product.views_count == 1

    def test_increment_views_multiple(self):
        product = ProductFactory()
        product.increment_views()
        product.increment_views()
        product.refresh_from_db()
        assert product.views_count == 2
