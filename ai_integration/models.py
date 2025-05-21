from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class AIModel(models.Model):
    """
    Model to track available AI models and their configurations
    """
    name = models.CharField(max_length=100)
    provider = models.CharField(max_length=50, choices=[
        ('huggingface', 'Hugging Face'),
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google'),
        ('custom', 'Custom'),
    ])
    model_id = models.CharField(max_length=200, help_text="Model identifier used in API calls")
    
    model_type = models.CharField(max_length=50, choices=[
        ('text_generation', 'Text Generation'),
        ('text_classification', 'Text Classification'),
        ('image_generation', 'Image Generation'),
        ('image_classification', 'Image Classification'),
        ('sentiment_analysis', 'Sentiment Analysis'),
        ('summarization', 'Summarization'),
        ('translation', 'Translation'),
        ('question_answering', 'Question Answering'),
    ])
    
    description = models.TextField()
    
    # Configuration
    max_tokens = models.PositiveIntegerField(default=512)
    temperature = models.FloatField(default=0.7)
    top_p = models.FloatField(default=0.9)
    
    # API settings
    api_endpoint = models.URLField(blank=True)
    requires_auth = models.BooleanField(default=True)
    rate_limit = models.PositiveIntegerField(default=60, help_text="Requests per minute")
    
    # Status
    is_active = models.BooleanField(default=True)
    last_tested = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.provider})"

    class Meta:
        unique_together = ['provider', 'model_id']
        ordering = ['provider', 'name']


class AIRequest(models.Model):
    """
    Track all AI API requests for monitoring and analytics
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_requests'
    )
    
    ai_model = models.ForeignKey(
        AIModel,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    
    # Request details
    request_type = models.CharField(max_length=50, choices=[
        ('blog_draft', 'Blog Draft Generation'),
        ('blog_improve', 'Blog Improvement'),
        ('seo_optimization', 'SEO Optimization'),
        ('image_generation', 'Image Generation'),
        ('content_analysis', 'Content Analysis'),
        ('tag_suggestion', 'Tag Suggestion'),
        ('title_generation', 'Title Generation'),
        ('grammar_check', 'Grammar Check'),
        ('tone_analysis', 'Tone Analysis'),
        ('summarization', 'Content Summarization'),
    ])
    
    # Input/Output
    input_text = models.TextField()
    output_text = models.TextField()
    prompt_template = models.TextField(blank=True, help_text="Template used for the prompt")
    
    # Additional parameters
    parameters = models.JSONField(default=dict, help_text="Additional parameters sent to AI model")
    
    # Performance metrics
    processing_time = models.FloatField(help_text="Processing time in seconds")
    tokens_used = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.000000)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='pending')
    
    error_message = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.request_type} by {self.user.username} at {self.created_at}"

    def mark_completed(self, output_text, tokens_used=0, cost=0):
        """Mark request as completed with results"""
        self.status = 'completed'
        self.output_text = output_text
        self.tokens_used = tokens_used
        self.cost = cost
        self.completed_at = timezone.now()
        self.save()

    def mark_failed(self, error_message):
        """Mark request as failed with error"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save()

    class Meta:
        ordering = ['-created_at']


class PromptTemplate(models.Model):
    """
    Reusable prompt templates for different AI tasks
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    template_type = models.CharField(max_length=50, choices=[
        ('blog_draft', 'Blog Draft Generation'),
        ('blog_improve', 'Blog Improvement'),
        ('seo_meta', 'SEO Meta Generation'),
        ('content_expand', 'Content Expansion'),
        ('content_summarize', 'Content Summarization'),
        ('title_generation', 'Title Generation'),
        ('tag_suggestion', 'Tag Suggestion'),
        ('tone_adjustment', 'Tone Adjustment'),
        ('grammar_fix', 'Grammar Correction'),
    ])
    
    # Template content with placeholders
    template_text = models.TextField(
        help_text="Use {variable_name} for placeholders that will be replaced"
    )
    
    # Variable definitions
    required_variables = models.JSONField(
        default=list,
        help_text="List of required variable names"
    )
    optional_variables = models.JSONField(
        default=list,
        help_text="List of optional variable names"
    )
    
    # AI model settings
    recommended_models = models.ManyToManyField(
        AIModel,
        blank=True,
        help_text="AI models that work best with this template"
    )
    
    default_temperature = models.FloatField(default=0.7)
    default_max_tokens = models.PositiveIntegerField(default=512)
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(default=0)
    avg_rating = models.FloatField(default=0.0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def render_template(self, **kwargs):
        """Render template with provided variables"""
        template = self.template_text
        
        # Check required variables
        missing_vars = []
        for var in self.required_variables:
            if var not in kwargs:
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required variables: {', '.join(missing_vars)}")
        
        # Replace variables in template
        for key, value in kwargs.items():
            placeholder = '{' + key + '}'
            template = template.replace(placeholder, str(value))
        
        return template

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['template_type', 'name']


class UserAIUsage(models.Model):
    """
    Track AI usage per user for quotas and billing
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='ai_usage'
    )
    
    # Monthly usage tracking
    current_month = models.DateField(default=timezone.now)
    requests_this_month = models.PositiveIntegerField(default=0)
    tokens_this_month = models.PositiveIntegerField(default=0)
    cost_this_month = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Lifetime usage
    total_requests = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Quota settings
    monthly_request_limit = models.PositiveIntegerField(default=100)
    monthly_token_limit = models.PositiveIntegerField(default=50000)
    monthly_cost_limit = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    
    # Status
    is_quota_exceeded = models.BooleanField(default=False)
    last_request_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def check_quota(self):
        """Check if user has exceeded any quotas"""
        current_month = timezone.now().date().replace(day=1)
        
        # Reset monthly counters if new month
        if self.current_month != current_month:
            self.current_month = current_month
            self.requests_this_month = 0
            self.tokens_this_month = 0
            self.cost_this_month = 0.00
            self.is_quota_exceeded = False
            self.save()
        
        # Check quotas
        if (self.requests_this_month >= self.monthly_request_limit or
            self.tokens_this_month >= self.monthly_token_limit or
            self.cost_this_month >= self.monthly_cost_limit):
            self.is_quota_exceeded = True
            self.save()
            return False
        
        return True

    def update_usage(self, tokens_used, cost):
        """Update usage statistics"""
        self.requests_this_month += 1
        self.tokens_this_month += tokens_used
        self.cost_this_month += cost
        
        self.total_requests += 1
        self.total_tokens += tokens_used
        self.total_cost += cost
        
        self.last_request_date = timezone.now()
        self.save()

    def __str__(self):
        return f"AI Usage for {self.user.username}"

    class Meta:
        verbose_name = "User AI Usage"
        verbose_name_plural = "User AI Usage"


class AIFeedback(models.Model):
    """
    User feedback on AI-generated content
    """
    ai_request = models.OneToOneField(
        AIRequest,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    # Rating
    quality_rating = models.IntegerField(
        choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)],
        help_text="Rate the quality of AI output (1-5 stars)"
    )
    
    usefulness_rating = models.IntegerField(
        choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)],
        help_text="Rate how useful the output was (1-5 stars)"
    )
    
    # Feedback details
    positive_aspects = models.TextField(
        blank=True,
        help_text="What did you like about the AI output?"
    )
    
    negative_aspects = models.TextField(
        blank=True,
        help_text="What could be improved?"
    )
    
    suggestions = models.TextField(
        blank=True,
        help_text="Any suggestions for improvement?"
    )
    
    # Usage
    content_used = models.BooleanField(
        default=False,
        help_text="Did you use the AI-generated content?"
    )
    
    modifications_made = models.TextField(
        blank=True,
        help_text="What modifications did you make to the content?"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for {self.ai_request.request_type} - {self.quality_rating} stars"

    class Meta:
        ordering = ['-created_at']


class ContentAnalysis(models.Model):
    """
    Store AI analysis results for content
    """
    content_type = models.CharField(max_length=50, choices=[
        ('blog_post', 'Blog Post'),
        ('project_description', 'Project Description'),
        ('portfolio_content', 'Portfolio Content'),
        ('general_text', 'General Text'),
    ])
    
    content_id = models.PositiveIntegerField(help_text="ID of the analyzed content")
    content_text = models.TextField()
    
    # Analysis results
    readability_score = models.FloatField(null=True, blank=True)
    sentiment_score = models.FloatField(null=True, blank=True)
    tone_classification = models.CharField(max_length=50, blank=True)
    
    # SEO analysis
    keyword_density = models.JSONField(default=dict)
    suggested_keywords = models.JSONField(default=list)
    meta_description_suggestion = models.TextField(blank=True)
    title_suggestions = models.JSONField(default=list)
    
    # Content metrics
    word_count = models.PositiveIntegerField(default=0)
    reading_time = models.PositiveIntegerField(default=0, help_text="Minutes")
    complexity_score = models.FloatField(null=True, blank=True)
    
    # Suggestions
    improvement_suggestions = models.JSONField(default=list)
    tag_suggestions = models.JSONField(default=list)
    
    analyzed_at = models.DateTimeField(auto_now_add=True)
    ai_model_used = models.ForeignKey(
        AIModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Analysis of {self.content_type} #{self.content_id}"

    class Meta:
        ordering = ['-analyzed_at']
        verbose_name_plural = "Content Analyses"


class AIGeneratedImage(models.Model):
    """
    Track AI-generated images for portfolio and blog
    """
    prompt = models.TextField(help_text="Text prompt used to generate the image")
    negative_prompt = models.TextField(blank=True, help_text="Negative prompt to avoid certain elements")
    
    ai_model = models.ForeignKey(
        AIModel,
        on_delete=models.CASCADE,
        related_name='generated_images'
    )
    
    # Generation parameters
    width = models.PositiveIntegerField(default=512)
    height = models.PositiveIntegerField(default=512)
    steps = models.PositiveIntegerField(default=20)
    guidance_scale = models.FloatField(default=7.5)
    seed = models.BigIntegerField(null=True, blank=True)
    
    # Generated image
    image_file = models.ImageField(upload_to='ai_generated/')
    thumbnail = models.ImageField(upload_to='ai_generated/thumbnails/', blank=True)
    
    # Usage tracking
    used_in_content = models.BooleanField(default=False)
    content_type = models.CharField(max_length=50, blank=True)
    content_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Generation details
    generation_time = models.FloatField(help_text="Time taken to generate (seconds)")
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.000000)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ai_generated_images'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Image: {self.prompt[:50]}..."

    class Meta:
        ordering = ['-created_at']