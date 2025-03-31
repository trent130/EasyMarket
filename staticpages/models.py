from django.db import models


class StaticPage(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(unique=True)
    is_published = models.BooleanField(default=True)  # Added field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.question


class ContactMessage(models.Model):
    '''
    /* Contact message information for the static pages information */
    '''
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message from {self.name}'


class Testimonial(models.Model):
    '''
    /* static pages model to store the Testimonial related information */
    '''
    author = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return f'Testimonial by {self.author}'


class FooterLinks(models.Model):
    '''
    /* the model to store the footer links */
    '''
    CHOICES = [
        ("quick_links", "quick_links"),
        ("categories", "categories")
    ]
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    url = models.CharField(max_length=250)
    category = models.CharField(max_length=150, choices=CHOICES)

    def __str__(self):
        return f"Footer links {self.title}"


class Address(models.Model):
    '''
    /* model to store the address information */

    '''
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"Address info {self.state}"


class ContactInfo(models.Model):
    '''
    /* models to store contact information for the footer links */
    /* it has a relationship with the address model */

    '''
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)
    email = models.EmailField()

    def __str__(self):
        return f"Our contact info {self.email}"


class Footer(models.Model):
    '''
    /* footer data storage models for the static page */

    '''
    quickLinks = models.ForeignKey(FooterLinks, on_delete=models.CASCADE)
    # categories = models.ForeignKey(FooterLinks, on_delete=models.CASCADE)
    contactInfo = models.ForeignKey(ContactInfo, on_delete=models.CASCADE)

    def __str__(self):
        return f"quick links {self.quicklinks}"

