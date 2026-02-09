from django.core.management.base import BaseCommand
from staticpages.models import StaticPage, FAQ, FooterLinks, Address, ContactInfo


class Command(BaseCommand):
    help = 'Seed static pages with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding static pages...')

        # Create Static Pages
        pages = [
            {
                'title': 'About Us',
                'slug': 'about',
                'content': 'EasyMarket is a student marketplace connecting buyers and sellers in the campus community.',
                'is_published': True
            },
            {
                'title': 'Privacy Policy',
                'slug': 'privacy',
                'content': 'Your privacy is important to us. We collect and use your data responsibly.',
                'is_published': True
            },
            {
                'title': 'Terms of Service',
                'slug': 'terms',
                'content': 'By using EasyMarket, you agree to our terms and conditions.',
                'is_published': True
            },
            {
                'title': 'Help Center',
                'slug': 'help',
                'content': 'Find answers to common questions and get support.',
                'is_published': True
            }
        ]

        for page_data in pages:
            StaticPage.objects.get_or_create(
                slug=page_data['slug'],
                defaults=page_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(pages)} static pages'))

        # Create FAQs
        faqs = [
            {
                'question': 'How do I create an account?',
                'answer': 'Click on Sign Up and fill in your details to create an account.',
                'is_published': True
            },
            {
                'question': 'How do I list a product?',
                'answer': 'Go to My Products and click Add Product to list your item.',
                'is_published': True
            },
            {
                'question': 'Is shipping available?',
                'answer': 'Shipping options depend on the seller. Check product details.',
                'is_published': True
            },
            {
                'question': 'How do I contact a seller?',
                'answer': 'Use the chat feature on the product page to message sellers.',
                'is_published': True
            }
        ]

        for faq_data in faqs:
            FAQ.objects.get_or_create(
                question=faq_data['question'],
                defaults=faq_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(faqs)} FAQs'))

        # Create Footer Quick Links
        quick_links = [
            {'title': 'About Us', 'url': '/about', 'slug': 'about', 'category': 'quick_links'},
            {'title': 'Contact', 'url': '/contact', 'slug': 'contact', 'category': 'quick_links'},
            {'title': 'Privacy Policy', 'url': '/privacy', 'slug': 'privacy', 'category': 'quick_links'},
            {'title': 'Terms of Service', 'url': '/terms', 'slug': 'terms', 'category': 'quick_links'},
        ]

        for link_data in quick_links:
            FooterLinks.objects.get_or_create(
                slug=link_data['slug'],
                defaults=link_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(quick_links)} quick links'))

        # Create Footer Categories
        categories = [
            {'title': 'Electronics', 'url': '/category?name=Electronics', 'slug': 'electronics', 'category': 'categories'},
            {'title': 'Books', 'url': '/category?name=Books', 'slug': 'books', 'category': 'categories'},
            {'title': 'Furniture', 'url': '/category?name=Furniture', 'slug': 'furniture', 'category': 'categories'},
            {'title': 'Clothing', 'url': '/category?name=Clothing', 'slug': 'clothing', 'category': 'categories'},
        ]

        for cat_data in categories:
            FooterLinks.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
        self.stdout.write(self.style.SUCCESS(f'Created {len(categories)} category links'))

        # Create Address and Contact Info
        address, _ = Address.objects.get_or_create(
            street='123 Campus Drive',
            defaults={
                'city': 'University City',
                'state': 'CA',
                'postal_code': '90210',
                'country': 'USA'
            }
        )

        ContactInfo.objects.get_or_create(
            address=address,
            defaults={
                'phone': '+1 (555) 123-4567',
                'email': 'support@easymarket.com'
            }
        )
        self.stdout.write(self.style.SUCCESS('Created contact info'))

        self.stdout.write(self.style.SUCCESS('Static pages seeded successfully!'))
