from rest_framework import serializers
from .models import StaticPage, FAQ, ContactMessage, Testimonial
from django.core.validators import EmailValidator

class StaticPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaticPage
        fields = ['id', 'title', 'slug', 'content', 'meta_description', 'is_published', 'updated_at']
        read_only_fields = ['slug', 'updated_at']

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'order', 'is_published']

class FAQCategorySerializer(serializers.Serializer):
    category = serializers.CharField()
    faqs = FAQSerializer(many=True, read_only=True)

class ContactMessageSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])
    
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'subject', 'message', 'created_at']
        read_only_fields = ['created_at']

    def validate_message(self, value):
        if len(value) < 10:
            raise serializers.ValidationError(
                "Message must be at least 10 characters long"
            )
        return value

class TestimonialSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    student_avatar = serializers.ImageField(source='student.userprofile.avatar', read_only=True)

    class Meta:
        model = Testimonial
        fields = [
            'id', 'student', 'student_name', 'student_avatar',
            'content', 'rating', 'is_featured', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

class SiteSettingsSerializer(serializers.Serializer):
    site_name = serializers.CharField()
    site_description = serializers.CharField()
    contact_email = serializers.EmailField()
    contact_phone = serializers.CharField()
    social_links = serializers.DictField(
        child=serializers.URLField(),
        required=False
    )
    analytics_id = serializers.CharField(required=False)
    maintenance_mode = serializers.BooleanField(default=False)

class NewsletterSubscriptionSerializer(serializers.Serializer):
    email = serializers.EmailField()
    name = serializers.CharField(required=False)
    interests = serializers.MultipleChoiceField(
        choices=['products', 'blog', 'promotions'],
        required=False
    )

    def validate_email(self, value):
        # Add custom email validation if needed
        return value.lower()

class FeedbackSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=['bug', 'feature', 'content', 'other']
    )
    subject = serializers.CharField(max_length=200)
    description = serializers.CharField()
    screenshot = serializers.ImageField(required=False)
    browser_info = serializers.JSONField(required=False)

class SitemapSerializer(serializers.Serializer):
    url = serializers.URLField()
    last_modified = serializers.DateTimeField()
    change_frequency = serializers.ChoiceField(
        choices=['always', 'hourly', 'daily', 'weekly', 'monthly', 'yearly', 'never']
    )
    priority = serializers.DecimalField(
        max_digits=2,
        decimal_places=1,
        min_value=0.0,
        max_value=1.0
    )

class MetaTagSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=60)
    description = serializers.CharField(max_length=160)
    keywords = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    og_title = serializers.CharField(max_length=60, required=False)
    og_description = serializers.CharField(max_length=200, required=False)
    og_image = serializers.URLField(required=False)
    twitter_card = serializers.ChoiceField(
        choices=['summary', 'summary_large_image'],
        required=False
    )
