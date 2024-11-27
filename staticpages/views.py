from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import StaticPage, FAQ, ContactMessage, Testimonial
from .serializers import (
    StaticPageSerializer,
    FAQSerializer,
    FAQCategorySerializer,
    ContactMessageSerializer,
    TestimonialSerializer,
    SiteSettingsSerializer,
    NewsletterSubscriptionSerializer,
    FeedbackSerializer,
    SitemapSerializer,
    MetaTagSerializer
)
import logging

logger = logging.getLogger(__name__)

class StaticPageViewSet(viewsets.ModelViewSet):
    queryset = StaticPage.objects.filter(is_published=True)
    serializer_class = StaticPageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            return StaticPage.objects.all()
        return queryset

    @action(detail=False, methods=['get'])
    def home(self, request):
        """Get home page content"""
        try:
            page = StaticPage.objects.get(slug='home')
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
            'description': page.meta_description,
            'keywords': page.meta_keywords.split(',') if page.meta_keywords else [],
            'og_title': page.title,
            'og_description': page.meta_description
        })
        return Response(serializer.data)

class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.filter(is_published=True)
    serializer_class = FAQSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get FAQs grouped by category"""
        categories = FAQ.objects.values_list(
            'category', flat=True
        ).distinct()
        
        result = []
        for category in categories:
            faqs = FAQ.objects.filter(
                category=category,
                is_published=True
            )
            serializer = FAQCategorySerializer({
                'category': category,
                'faqs': faqs
            })
            result.append(serializer.data)
            
        return Response(result)

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search FAQs"""
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
            
        faqs = FAQ.objects.filter(
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
                'subject': serializer.validated_data['subject'],
                'message': serializer.validated_data['message']
            }
            
            html_message = render_to_string(
                'emails/contact_notification.html',
                context
            )
            plain_message = strip_tags(html_message)
            
            send_mail(
                f"Contact Form: {serializer.validated_data['subject']}",
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
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return queryset.order_by('-created_at')[:6]
        return queryset

    def perform_create(self, serializer):
        serializer.save(student=self.request.user.student)

class SiteSettingsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        """Get site settings"""
        cache_key = 'site_settings'
        settings = cache.get(cache_key)
        
        if not settings:
            settings = {
                'site_name': settings.SITE_NAME,
                'site_description': settings.SITE_DESCRIPTION,
                'contact_email': settings.CONTACT_EMAIL,
                'contact_phone': settings.CONTACT_PHONE,
                'social_links': settings.SOCIAL_LINKS,
                'maintenance_mode': settings.MAINTENANCE_MODE
            }
            cache.set(cache_key, settings, 3600)  # Cache for 1 hour
            
        serializer = SiteSettingsSerializer(settings)
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
