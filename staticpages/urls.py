from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'pages', views.StaticPageViewSet, basename='page')
router.register(r'faqs', views.FAQViewSet, basename='faq')
router.register(r'contact', views.ContactMessageViewSet, basename='contact')
router.register(r'testimonials', views.TestimonialViewSet, basename='testimonial')

urlpatterns = [
    # Router URLs
    path('api/', include(router.urls)),

    # Static Pages
    path('api/pages/home/',
         views.StaticPageViewSet.as_view({'get': 'home'}),
         name='home-page'),
    
    path('api/pages/<slug:slug>/meta/',
         views.StaticPageViewSet.as_view({'get': 'meta'}),
         name='page-meta'),

    # FAQs
    path('api/faqs/categories/',
         views.FAQViewSet.as_view({'get': 'by_category'}),
         name='faq-categories'),
    
    path('api/faqs/search/',
         views.FAQViewSet.as_view({'get': 'search'}),
         name='faq-search'),

    # Site Settings
    path('api/settings/',
         views.SiteSettingsViewSet.as_view({'get': 'list'}),
         name='site-settings'),

    # Newsletter
    path('api/newsletter/subscribe/',
         views.NewsletterViewSet.as_view({'post': 'create'}),
         name='newsletter-subscribe'),

    # Feedback
    path('api/feedback/',
         views.FeedbackViewSet.as_view({'post': 'create'}),
         name='submit-feedback'),

    # Content Management
    path('api/pages/preview/<slug:slug>/',
         views.StaticPageViewSet.as_view({'get': 'preview'}),
         name='preview-page'),
    
    path('api/pages/publish/<slug:slug>/',
         views.StaticPageViewSet.as_view({'post': 'publish'}),
         name='publish-page'),
    
    path('api/pages/unpublish/<slug:slug>/',
         views.StaticPageViewSet.as_view({'post': 'unpublish'}),
         name='unpublish-page'),

    # Testimonials Management
    path('api/testimonials/featured/',
         views.TestimonialViewSet.as_view({'get': 'featured'}),
         name='featured-testimonials'),
    
    path('api/testimonials/approve/<int:pk>/',
         views.TestimonialViewSet.as_view({'post': 'approve'}),
         name='approve-testimonial'),
    
    path('api/testimonials/reject/<int:pk>/',
         views.TestimonialViewSet.as_view({'post': 'reject'}),
         name='reject-testimonial'),

    # Contact Form
    path('api/contact/departments/',
         views.ContactMessageViewSet.as_view({'get': 'departments'}),
         name='contact-departments'),
    
    path('api/contact/support/',
         views.ContactMessageViewSet.as_view({'post': 'support'}),
         name='contact-support'),

    # SEO Management
    path('api/seo/sitemap/',
         views.StaticPageViewSet.as_view({'get': 'sitemap'}),
         name='sitemap'),
    
    path('api/seo/robots/',
         views.StaticPageViewSet.as_view({'get': 'robots'}),
         name='robots'),
    
    path('api/seo/meta-tags/',
         views.StaticPageViewSet.as_view({'get': 'meta_tags'}),
         name='meta-tags'),

    # Cache Management
    path('api/cache/clear/',
         views.SiteSettingsViewSet.as_view({'post': 'clear_cache'}),
         name='clear-cache'),
    
    path('api/cache/warm/',
         views.SiteSettingsViewSet.as_view({'post': 'warm_cache'}),
         name='warm-cache'),

    # Analytics
    path('api/analytics/page-views/',
         views.StaticPageViewSet.as_view({'get': 'page_views'}),
         name='page-views'),
    
    path('api/analytics/popular-pages/',
         views.StaticPageViewSet.as_view({'get': 'popular_pages'}),
         name='popular-pages'),
]

# Add debug patterns if in debug mode
from django.conf import settings
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
