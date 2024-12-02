from django.core.cache import cache
from django.conf import settings
from django.utils.text import slugify
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging
import json
import re

logger = logging.getLogger(__name__)

# Cache keys
PAGE_CACHE_KEY = 'page_{slug}'
FAQ_CACHE_KEY = 'faqs_{category}'
SETTINGS_CACHE_KEY = 'site_settings'
META_CACHE_KEY = 'meta_{page_id}'

# Cache timeouts (in seconds)
PAGE_CACHE_TIMEOUT = 3600  # 1 hour
FAQ_CACHE_TIMEOUT = 3600  # 1 hour
SETTINGS_CACHE_TIMEOUT = 86400  # 24 hours
META_CACHE_TIMEOUT = 3600  # 1 hour

def get_cached_page(slug):
    """Get page from cache or database"""
    cache_key = PAGE_CACHE_KEY.format(slug=slug)
    page_data = cache.get(cache_key)
    
    if page_data is None:
        from .models import StaticPage
        try:
            page = StaticPage.objects.get(slug=slug, is_published=True)
            page_data = {
                'title': page.title,
                'content': page.content,
                'meta_description': page.meta_description,
                'updated_at': page.updated_at.isoformat()
            }
            cache.set(cache_key, page_data, PAGE_CACHE_TIMEOUT)
        except StaticPage.DoesNotExist:
            return None
            
    return page_data

def clear_page_cache(slug):
    """Clear page cache"""
    cache_key = PAGE_CACHE_KEY.format(slug=slug)
    cache.delete(cache_key)

def get_cached_faqs(category=None):
    """Get FAQs from cache or database"""
    cache_key = FAQ_CACHE_KEY.format(category=category or 'all')
    faqs_data = cache.get(cache_key)
    
    if faqs_data is None:
        from .models import FAQ
        queryset = FAQ.objects.filter(is_published=True)
        if category:
            queryset = queryset.filter(category=category)
            
        faqs_data = list(queryset.values(
            'question', 'answer', 'category', 'order'
        ))
        cache.set(cache_key, faqs_data, FAQ_CACHE_TIMEOUT)
        
    return faqs_data

def clear_faq_cache(category=None):
    """Clear FAQ cache"""
    if category:
        cache_key = FAQ_CACHE_KEY.format(category=category)
        cache.delete(cache_key)
    else:
        # Clear all FAQ caches
        cache.delete_pattern(FAQ_CACHE_KEY.format(category='*'))

def get_site_settings():
    """Get site settings from cache or settings"""
    settings_data = cache.get(SETTINGS_CACHE_KEY)
    
    if settings_data is None:
        settings_data = {
            'site_name': settings.SITE_NAME,
            'site_description': settings.SITE_DESCRIPTION,
            'contact_email': settings.CONTACT_EMAIL,
            'contact_phone': settings.CONTACT_PHONE,
            'social_links': settings.SOCIAL_LINKS,
            'maintenance_mode': settings.MAINTENANCE_MODE
        }
        cache.set(SETTINGS_CACHE_KEY, settings_data, SETTINGS_CACHE_TIMEOUT)
        
    return settings_data

def clear_site_settings_cache():
    """Clear site settings cache"""
    cache.delete(SETTINGS_CACHE_KEY)

def send_contact_notification(contact_data):
    """Send contact form notification email"""
    try:
        context = {
            'name': contact_data['name'],
            'email': contact_data['email'],
            'subject': contact_data['subject'],
            'message': contact_data['message']
        }
        
        html_content = render_to_string(
            'emails/contact_notification.html',
            context
        )
        text_content = strip_tags(html_content)
        
        msg = EmailMultiAlternatives(
            subject=f"Contact Form: {contact_data['subject']}",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
        return True
    except Exception as e:
        logger.error(f"Failed to send contact notification: {str(e)}")
        return False

def generate_meta_tags(page):
    """Generate meta tags for a page"""
    meta_data = cache.get(META_CACHE_KEY.format(page_id=page.id))
    
    if meta_data is None:
        meta_data = {
            'title': page.title,
            'description': page.meta_description,
            'keywords': page.meta_keywords.split(',') if page.meta_keywords else [],
            'og_title': page.title,
            'og_description': page.meta_description,
            'og_type': 'website',
            'og_url': f"{settings.SITE_URL}/pages/{page.slug}/",
            'twitter_card': 'summary'
        }
        cache.set(META_CACHE_KEY.format(page_id=page.id), meta_data, META_CACHE_TIMEOUT)
        
    return meta_data

def clear_meta_cache(page_id):
    """Clear meta tags cache"""
    cache.delete(META_CACHE_KEY.format(page_id=page_id))

def generate_sitemap_data():
    """Generate sitemap data"""
    from .models import StaticPage
    pages = StaticPage.objects.filter(is_published=True)
    
    sitemap_data = []
    for page in pages:
        sitemap_data.append({
            'url': f"{settings.SITE_URL}/pages/{page.slug}/",
            'last_modified': page.updated_at.isoformat(),
            'change_frequency': 'weekly',
            'priority': 0.8 if page.slug == 'home' else 0.5
        })
        
    return sitemap_data

def sanitize_html(content):
    """Sanitize HTML content"""
    # Remove script tags and their content
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    
    # Remove style tags and their content
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
    
    # Remove onclick and other JavaScript event handlers
    content = re.sub(r' on\w+="[^"]*"', '', content)
    
    # Remove iframe tags
    content = re.sub(r'<iframe[^>]*>.*?</iframe>', '', content, flags=re.DOTALL)
    
    return content.strip()

def track_page_view(page_slug):
    """Track page view for analytics"""
    try:
        from .models import PageView
        PageView.objects.create(page_slug=page_slug)
        return True
    except Exception as e:
        logger.error(f"Failed to track page view: {str(e)}")
        return False

def get_popular_pages(days=30, limit=10):
    """Get popular pages based on views"""
    from .models import PageView
    from django.db.models import Count
    from django.utils import timezone
    import datetime
    
    start_date = timezone.now() - datetime.timedelta(days=days)
    
    popular_pages = PageView.objects.filter(
        created_at__gte=start_date
    ).values(
        'page_slug'
    ).annotate(
        view_count=Count('id')
    ).order_by(
        '-view_count'
    )[:limit]
    
    return list(popular_pages)
