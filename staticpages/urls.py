from django.urls import path, include
from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()
router.register(r'pages', views.StaticPageViewSet, basename='page')
router.register(r'faqs', views.FAQViewSet, basename='faq')
router.register(r'contact', views.ContactMessageViewSet, basename='contact')
router.register(r'testimonials', views.TestimonialViewSet, basename='testimonial')

urlpatterns = [
    # Footer
    path('footer/', views.get_footer_data, name='footer-data'),

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

    # Featured testimonials
    # The viewset has no separate featured action, but its list queryset is
    # already limited to featured testimonials.
    path('testimonials/featured/',
         views.TestimonialViewSet.as_view({'get': 'list'}),
         name='featured-testimonials'),

    # Router URLs are fallbacks for the standard viewset endpoints. They
    # must follow explicit routes such as pages/home/ and faqs/search/.
    path('', include(router.urls)),
]
