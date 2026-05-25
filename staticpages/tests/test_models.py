import pytest
from staticpages.models import (
    StaticPage, Faq, ContactMessage, Testimonial,
    FooterLinks, Address, ContactInfo, Footer
)
from tests.factories import CustomUserFactory


pytestmark = pytest.mark.django_db


class TestStaticPageModel:
    def test_str(self):
        page = StaticPage.objects.create(title="About Us", content="Content", slug="about-us")
        assert str(page) == "About Us"


class TestFaqModel:
    def test_str(self):
        faq = Faq.objects.create(question="What is this?", answer="That")
        assert str(faq) == "What is this?"


class TestContactMessageModel:
    def test_str(self):
        msg = ContactMessage.objects.create(name="John", email="j@example.com", message="Hi")
        assert str(msg) == "Message from John"


class TestTestimonialModel:
    def test_str(self):
        user = CustomUserFactory()
        t = Testimonial.objects.create(author=user, content="Great!")
        assert "Testimonial by" in str(t)


class TestFooterLinksModel:
    def test_str(self):
        link = FooterLinks.objects.create(slug="privacy", title="Privacy Policy", url="/privacy/", category="quick_links")
        assert str(link) == "Footer links Privacy Policy"


class TestAddressModel:
    def test_str(self):
        addr = Address.objects.create(street="123 Main", city="Nairobi", state="Nairobi", postal_code="00100", country="Kenya")
        assert "Address info" in str(addr)


class TestContactInfoModel:
    def test_str(self):
        addr = Address.objects.create(street="123 Main", city="Nairobi", state="Nairobi", postal_code="00100", country="Kenya")
        ci = ContactInfo.objects.create(address=addr, phone="+254700000000", email="info@example.com")
        assert "Our contact info" in str(ci)


class TestFooterModel:
    def test_str(self):
        link = FooterLinks.objects.create(slug="privacy", title="Privacy Policy", url="/privacy/", category="quick_links")
        addr = Address.objects.create(street="123 Main", city="Nairobi", state="Nairobi", postal_code="00100", country="Kenya")
        ci = ContactInfo.objects.create(address=addr, phone="+254700000000", email="info@example.com")
        footer = Footer.objects.create(quickLinks=link, contactInfo=ci)
        assert "Footer with quick links" in str(footer)
