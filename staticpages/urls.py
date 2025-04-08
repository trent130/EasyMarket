from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from django.conf import settings

router = DefaultRouter()
router.register(r'pages', views.StaticPageViewSet, basename='page')
router.register(r'faqs', views.FAQViewSet, basename='faq')
router.register(r'contact', views.ContactMessageViewSet, basename='contact')
router.register(r'testimonials', views.TestimonialViewSet, basename='testimonial')

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Static Pages
    path('pages/home/',
         views.StaticPageViewSet.as_view({'get': 'home'}),
         name='home-page'),
    path('pages/<slug:slug>/meta/',
         views.StaticPageViewSet.as_view({'get': 'meta'}),
         name='page-meta'),

    # FAQs
    path('faqs/categories/',
         views.FAQViewSet.as_view({'get': 'by_category'}),
         name='faq-categories'),
    path('faqs/search/',
         views.FAQViewSet.as_view({'get': 'search'}),
         name='faq-search'),

    # Site Settings
    path('settings/',
         views.SiteSettingsViewSet.as_view({'get': 'list'}),
         name='site-settings'),

    # Newsletter
    path('newsletter/subscribe/',
         views.NewsletterViewSet.as_view({'post': 'create'}),
         name='newsletter-subscribe'),

    # Feedback
    path('feedback/',
         views.FeedbackViewSet.as_view({'post': 'create'}),
         name='submit-feedback'),

    # Content Management
    path('pages/preview/<slug:slug>/',
         views.StaticPageViewSet.as_view({'get': 'preview'}),
         name='preview-page'),
    path('pages/publish/<slug:slug>/',
         views.StaticPageViewSet.as_view({'post': 'publish'}),
         name='publish-page'),
    path('pages/unpublish/<slug:slug>/',
         views.StaticPageViewSet.as_view({'post': 'unpublish'}),
         name='unpublish-page'),

    # Testimonials Management
    path('testimonials/featured/',
         views.TestimonialViewSet.as_view({'get': 'featured'}),
         name='featured-testimonials'),
    path('testimonials/approve/<int:pk>/',
         views.TestimonialViewSet.as_view({'post': 'approve'}),
         name='approve-testimonial'),
    path('testimonials/reject/<int:pk>/',
         views.TestimonialViewSet.as_view({'post': 'reject'}),
         name='reject-testimonial'),

    # Contact Form
    path('contact/departments/',
         views.ContactMessageViewSet.as_view({'get': 'departments'}),
         name='contact-departments'),
    path('contact/support/',
         views.ContactMessageViewSet.as_view({'post': 'support'}),
         name='contact-support'),

    # SEO Management
    path('seo/sitemap/',
         views.StaticPageViewSet.as_view({'get': 'sitemap'}),
         name='sitemap'),
    path('seo/robots/',
         views.StaticPageViewSet.as_view({'get': 'robots'}),
         name='robots'),
    path('seo/meta-tags/',
         views.StaticPageViewSet.as_view({'get': 'meta_tags'}),
         name='meta-tags'),

    # Cache Management
    path('cache/clear/',
         views.SiteSettingsViewSet.as_view({'post': 'clear_cache'}),
         name='clear-cache'),
    path('cache/warm/',
         views.SiteSettingsViewSet.as_view({'post': 'warm_cache'}),
         name='warm-cache'),

    # Analytics
    path('analytics/page-views/',
         views.StaticPageViewSet.as_view({'get': 'page_views'}),
         name='page-views'),
    path('analytics/popular-pages/',
         views.StaticPageViewSet.as_view({'get': 'popular_pages'}),
         name='popular-pages'),
]

# Add debug patterns if in debug mode
if settings.DEBUG:
    urlpatterns += [
        # Preview URLs
        path('api/preview/pages/<slug:slug>/',
             views.StaticPageViewSet.as_view({'get': 'preview_draft'}),
             name='preview-draft'),
        # Test URLs
        path('api/test/contact/',
             views.ContactMessageViewSet.as_view({'post': 'test_contact'}),
             name='test-contact'),
        path('api/test/newsletter/',
             views.NewsletterViewSet.as_view({'post': 'test_subscribe'}),
             name='test-newsletter'),
    ]
