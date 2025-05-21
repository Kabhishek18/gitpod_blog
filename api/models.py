from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string


class APIKey(models.Model):
    """
    Model for managing API keys for external access
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Descriptive name for this API key"
    )
    
    key = models.CharField(
        max_length=64,
        unique=True,
        help_text="The actual API key"
    )
    
    # Permissions
    permissions = models.JSONField(default=dict, help_text="API permissions as JSON")
    
    # Usage tracking
    total_requests = models.PositiveIntegerField(default=0)
    requests_today = models.PositiveIntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    last_used_ip = models.GenericIPAddressField(null=True, blank=True)
    
    # Rate limiting
    rate_limit_per_hour = models.PositiveIntegerField(default=1000)
    rate_limit_per_day = models.PositiveIntegerField(default=10000)
    
    # Status
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_api_key()
        super().save(*args, **kwargs)

    def generate_api_key(self):
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    def is_valid(self):
        """Check if API key is valid and not expired"""
        if not self.is_active:
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            return False
        
        return True

    def increment_usage(self, ip_address=None):
        """Increment usage counters"""
        self.total_requests += 1
        self.requests_today += 1
        self.last_used = timezone.now()
        if ip_address:
            self.last_used_ip = ip_address
        self.save()

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    class Meta:
        ordering = ['-created_at']


class APIRequest(models.Model):
    """
    Log all API requests for monitoring and analytics
    """
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        related_name='requests',
        null=True,
        blank=True
    )
    
    # Request details
    method = models.CharField(max_length=10)
    endpoint = models.CharField(max_length=200)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    
    # Request/Response data
    request_data = models.JSONField(default=dict, help_text="Request payload")
    response_data = models.JSONField(default=dict, help_text="Response payload")
    
    # Performance metrics
    response_time = models.FloatField(help_text="Response time in milliseconds")
    status_code = models.PositiveIntegerField()
    
    # Error tracking
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.status_code}"

    class Meta:
        ordering = ['-created_at']


class WebhookEndpoint(models.Model):
    """
    Webhook endpoints for third-party integrations
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='webhook_endpoints'
    )
    
    name = models.CharField(max_length=100)
    url = models.URLField()
    
    # Events to listen for
    events = models.JSONField(
        default=list,
        help_text="List of events this webhook should receive"
    )
    
    # Security
    secret = models.CharField(
        max_length=64,
        help_text="Secret for webhook signature verification"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_triggered = models.DateTimeField(null=True, blank=True)
    total_deliveries = models.PositiveIntegerField(default=0)
    failed_deliveries = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = self.generate_secret()
        super().save(*args, **kwargs)

    def generate_secret(self):
        """Generate webhook secret"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))

    def __str__(self):
        return f"{self.name} - {self.url}"

    class Meta:
        ordering = ['-created_at']


class WebhookDelivery(models.Model):
    """
    Track webhook delivery attempts
    """
    webhook_endpoint = models.ForeignKey(
        WebhookEndpoint,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    
    # Delivery details
    status_code = models.PositiveIntegerField(null=True, blank=True)
    response_body = models.TextField(blank=True)
    response_headers = models.JSONField(default=dict)
    
    # Timing
    delivery_time = models.FloatField(null=True, blank=True, help_text="Delivery time in milliseconds")
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ], default='pending')
    
    attempt_count = models.PositiveIntegerField(default=1)
    max_attempts = models.PositiveIntegerField(default=3)
    
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.event_type} to {self.webhook_endpoint.name} - {self.status}"

    class Meta:
        ordering = ['-created_at']


class CacheEntry(models.Model):
    """
    Custom cache model for API responses
    """
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField()
    
    # Cache metadata
    content_type = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list, help_text="Cache tags for invalidation")
    
    # Expiration
    expires_at = models.DateTimeField()
    
    # Usage tracking
    hit_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        """Check if cache entry is expired"""
        return timezone.now() > self.expires_at

    def increment_hit_count(self):
        """Increment hit count and update last accessed"""
        self.hit_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['hit_count', 'last_accessed'])

    def __str__(self):
        return f"Cache: {self.key}"

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Cache Entries"


class RateLimitEntry(models.Model):
    """
    Track rate limiting for API requests
    """
    identifier = models.CharField(
        max_length=255,
        help_text="IP address, API key, or user identifier"
    )
    
    endpoint = models.CharField(max_length=200)
    
    # Rate limit tracking
    request_count = models.PositiveIntegerField(default=1)
    window_start = models.DateTimeField(default=timezone.now)
    window_duration = models.PositiveIntegerField(default=3600, help_text="Window duration in seconds")
    
    # Limits
    limit_per_window = models.PositiveIntegerField(default=1000)
    
    # Status
    is_blocked = models.BooleanField(default=False)
    blocked_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_limit_exceeded(self):
        """Check if rate limit is exceeded"""
        return self.request_count >= self.limit_per_window

    def reset_if_expired(self):
        """Reset counter if window has expired"""
        window_end = self.window_start + timezone.timedelta(seconds=self.window_duration)
        if timezone.now() > window_end:
            self.request_count = 1
            self.window_start = timezone.now()
            self.is_blocked = False
            self.blocked_until = None
            self.save()
            return True
        return False

    def increment_count(self):
        """Increment request count"""
        if not self.reset_if_expired():
            self.request_count += 1
            if self.is_limit_exceeded():
                self.is_blocked = True
                self.blocked_until = self.window_start + timezone.timedelta(seconds=self.window_duration)
            self.save()

    def __str__(self):
        return f"Rate limit for {self.identifier} on {self.endpoint}"

    class Meta:
        unique_together = ['identifier', 'endpoint']
        ordering = ['-updated_at']


class APIAnalytics(models.Model):
    """
    Daily analytics for API usage
    """
    date = models.DateField(unique=True)
    
    # Request counts
    total_requests = models.PositiveIntegerField(default=0)
    successful_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    
    # Response times
    avg_response_time = models.FloatField(default=0.0)
    min_response_time = models.FloatField(default=0.0)
    max_response_time = models.FloatField(default=0.0)
    
    # Popular endpoints
    top_endpoints = models.JSONField(default=dict)
    
    # Error analysis
    error_rates = models.JSONField(default=dict)
    common_errors = models.JSONField(default=list)
    
    # User activity
    unique_users = models.PositiveIntegerField(default=0)
    unique_api_keys = models.PositiveIntegerField(default=0)
    
    # Traffic sources
    traffic_by_country = models.JSONField(default=dict)
    user_agents = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"API Analytics for {self.date}"

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "API Analytics"


class ExternalService(models.Model):
    """
    Configuration for external service integrations
    """
    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50, choices=[
        ('email', 'Email Service'),
        ('storage', 'Storage Service'),
        ('cdn', 'CDN Service'),
        ('analytics', 'Analytics Service'),
        ('social', 'Social Media'),
        ('payment', 'Payment Gateway'),
        ('notification', 'Notification Service'),
        ('other', 'Other'),
    ])
    
    # Connection details
    api_endpoint = models.URLField()
    api_key = models.CharField(max_length=200, blank=True)
    api_secret = models.CharField(max_length=200, blank=True)
    
    # Configuration
    configuration = models.JSONField(
        default=dict,
        help_text="Service-specific configuration as JSON"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    last_tested = models.DateTimeField(null=True, blank=True)
    test_status = models.CharField(max_length=20, choices=[
        ('unknown', 'Unknown'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], default='unknown')
    
    # Usage tracking
    total_requests = models.PositiveIntegerField(default=0)
    failed_requests = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def test_connection(self):
        """Test connection to external service"""
        # Implementation would depend on service type
        # This is a placeholder method
        pass

    def __str__(self):
        return f"{self.name} ({self.service_type})"

    class Meta:
        ordering = ['service_type', 'name']


class APIDocumentation(models.Model):
    """
    Store API documentation and examples
    """
    endpoint = models.CharField(max_length=200)
    method = models.CharField(max_length=10, choices=[
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ])
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Parameters
    path_parameters = models.JSONField(default=list)
    query_parameters = models.JSONField(default=list)
    body_parameters = models.JSONField(default=list)
    
    # Examples
    request_example = models.JSONField(default=dict)
    response_example = models.JSONField(default=dict)
    
    # Additional info
    authentication_required = models.BooleanField(default=True)
    rate_limit = models.CharField(max_length=100, blank=True)
    
    # Status
    is_deprecated = models.BooleanField(default=False)
    version = models.CharField(max_length=10, default='1.0')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.title}"

    class Meta:
        unique_together = ['endpoint', 'method']
        ordering = ['endpoint', 'method']