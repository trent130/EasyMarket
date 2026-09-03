from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import StaticPage, Faq, ContactMessage, Testimonial, FooterLinks, ContactInfo
from .serializers import (
    StaticPageSerializer,
    FaqSerializer,
    FaqCategorySerializer,
    ContactMessageSerializer,
    TestimonialSerializer,
    SiteSettingsSerializer,
    NewsletterSubscriptionSerializer,
    FeedbackSerializer,
    MetaTagSerializer,
    FooterDataSerializer,
    FooterLinksSerializer,
    ContactInfoSerializer
)
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_footer_data(request):
    links = FooterLinks.objects.all()[:5]
    contact = ContactInfo.objects.first()
    data = FooterDataSerializer({
        "quickLinks": links,
        "categories": links,
        "contactInfo": contact or {},
    }).data
    return Response(data)


class StaticPageViewSet(viewsets.ModelViewSet):
    queryset = StaticPage.objects.filter(is_published=True)
    serializer_class = StaticPageSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_permissions(self):
        if self.action in {'list', 'retrieve', 'home', 'meta'}:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return StaticPage.objects.all()
        return queryset

    @action(detail=False, methods=['get'])
    def home(self, request):
        """Get home page content"""
        try:
            page = StaticPage.objects.get(slug='home', is_published=True)
            serializer = self.get_serializer(page)
            return Response(serializer.data)
        except StaticPage.DoesNotExist:
            return Response(
                {'error': 'Home page not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def meta(self, request, slug=None):
        """Get page meta tags"""
        page = self.get_object()
        serializer = MetaTagSerializer({
            'title': page.title,
            'description': page.content,
            'keywords': [],
            'og_title': page.title,
            'og_description': page.content
        })
        return Response(serializer.data)


class FAQViewSet(viewsets.ModelViewSet):
    queryset = Faq.objects.filter(is_published=True)
    serializer_class = FaqSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in {'list', 'retrieve', 'by_category', 'search'}:
            return [AllowAny()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get all published FAQs (Faq model has no category field)"""
        faqs = Faq.objects.filter(is_published=True)
        serializer = self.get_serializer(faqs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search FAQs"""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        faqs = Faq.objects.filter(
            is_published=True
        ).filter(
            question__icontains=query
        )
        serializer = self.get_serializer(faqs, many=True)
        return Response(serializer.data)


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]
    http_method_names = ['post', 'head']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Send email notification
        try:
            context = {
                'name': serializer.validated_data['name'],
                'email': serializer.validated_data['email'],
                'message': serializer.validated_data['message']
            }
            html_message = render_to_string(
                'emails/contact_notification.html',
                context
            )
            plain_message = strip_tags(html_message)
            send_mail(
                f"Contact Form: {serializer.validated_data['name']}",
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                html_message=html_message
            )
        except Exception as e:
            logger.error(f"Failed to send contact notification: {str(e)}")

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.filter(is_featured=True)
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.order_by('-created_at')[:6]
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class SiteSettingsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        """Get site settings"""
        cache_key = 'site_settings'
        site_settings = cache.get(cache_key)
        if not site_settings:
            site_settings = {
                'site_name': settings.SITE_NAME,
                'site_description': settings.SITE_DESCRIPTION,
                'contact_email': settings.CONTACT_EMAIL,
                'contact_phone': settings.CONTACT_PHONE,
                'social_links': settings.SOCIAL_LINKS,
                'maintenance_mode': settings.MAINTENANCE_MODE
            }
            cache.set(cache_key, site_settings, 3600)  # Cache for 1 hour
        serializer = SiteSettingsSerializer(site_settings)
        return Response(serializer.data)


class NewsletterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def create(self, request):
        """Subscribe to newsletter"""
        serializer = NewsletterSubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            # Implement newsletter subscription logic
            # (e.g., using a service like Mailchimp)
            return Response({'status': 'subscribed'})
        except Exception as e:
            logger.error(f"Newsletter subscription failed: {str(e)}")
            return Response(
                {'error': 'Subscription failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FeedbackViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Submit feedback"""
        serializer = FeedbackSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            # Store feedback and notify administrators
            return Response({'status': 'received'})
        except Exception as e:
            logger.error(f"Feedback submission failed: {str(e)}")
            return Response(
                {'error': 'Submission failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class FooterViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        """Get footer data including links and contact info"""
        try:
            from .models import FooterLinks, ContactInfo, Address

            # Get footer links grouped by category
            quick_links = FooterLinks.objects.filter(category='quick_links')
            categories = FooterLinks.objects.filter(category='categories')

            # Get contact info (assuming there's at least one)
            contact_info = ContactInfo.objects.select_related('address').first()

            footer_data = {
                'quick_links': [
                    {
                        'title': link.title,
                        'url': link.url,
                        'slug': link.slug
                    } for link in quick_links
                ],
                'categories': [
                    {
                        'title': link.title,
                        'url': link.url,
                        'slug': link.slug
                    } for link in categories
                ],
                'contact_info': None
            }

            if contact_info:
                footer_data['contact_info'] = {
                    'phone': contact_info.phone,
                    'email': contact_info.email,
                    'address': {
                        'street': contact_info.address.street,
                        'city': contact_info.address.city,
                        'state': contact_info.address.state,
                        'postal_code': contact_info.address.postal_code,
                        'country': contact_info.address.country
                    }
                }

            return Response(footer_data)

        except Exception as e:
            logger.error(f"Error fetching footer data: {str(e)}")
            # Return default footer data if there's an error
            return Response({
                'quick_links': [],
                'categories': [],
                'contact_info': None
            })
