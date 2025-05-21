from rest_framework import serializers
from blog.models import BlogPage, BlogCategory, BlogAuthor
from ai_integration.models import AIModel, AIRequest


class BlogCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for blog categories
    """
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description', 'color', 'post_count']
    
    def get_post_count(self, obj):
        return obj.blogpage_set.filter(is_draft=False).count()


class BlogAuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for blog authors
    """
    avatar_url = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogAuthor
        fields = [
            'id', 'full_name', 'bio', 'avatar_url', 'website', 
            'twitter', 'linkedin', 'github', 'posts_count', 'total_views'
        ]
    
    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.file.url)
        return None
    
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class BlogPageSerializer(serializers.ModelSerializer):
    """
    Serializer for blog posts (list view)
    """
    author = serializers.SerializerMethodField()
    categories = BlogCategorySerializer(many=True, read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    social_image_url = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True, read_only=True)
    excerpt_text = serializers.CharField(source='excerpt', read_only=True)
    
    class Meta:
        model = BlogPage
        fields = [
            'id', 'title', 'slug', 'excerpt_text', 'featured_image_url',
            'social_image_url', 'author', 'publish_date', 'categories', 'tags',
            'meta_description', 'reading_time', 'view_count', 'url',
            'first_published_at', 'last_published_at', 'tone_analysis',
            'ai_content_score'
        ]
    
    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'full_name': obj.author.get_full_name() or obj.author.username,
            'email': obj.author.email
        }
    
    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.file.url)
        return None
    
    def get_social_image_url(self, obj):
        image = obj.social_image or obj.featured_image
        if image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image.file.url)
        return None
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.url)
        return obj.url


class BlogPageDetailSerializer(BlogPageSerializer):
    """
    Serializer for blog posts (detail view)
    """
    body_text = serializers.SerializerMethodField()
    body_html = serializers.SerializerMethodField()
    related_posts = serializers.SerializerMethodField()
    word_count = serializers.SerializerMethodField()
    
    class Meta(BlogPageSerializer.Meta):
        fields = BlogPageSerializer.Meta.fields + [
            'body_text', 'body_html', 'related_posts', 'word_count',
            'ai_generated_summary', 'ai_suggested_tags', 'ai_seo_keywords'
        ]
    
    def get_body_text(self, obj):
        """Extract plain text content from StreamField"""
        text_content = []
        if obj.body:
            for block in obj.body:
                if hasattr(block.value, 'source'):
                    # Rich text block - strip HTML tags
                    import re
                    clean_text = re.sub('<[^<]+?>', '', block.value.source)
                    text_content.append(clean_text)
                elif isinstance(block.value, str):
                    # Simple text block
                    text_content.append(block.value)
        return '\n\n'.join(text_content)
    
    def get_body_html(self, obj):
        """Get HTML content from StreamField"""
        html_content = []
        if obj.body:
            for block in obj.body:
                if hasattr(block.value, 'source'):
                    # Rich text block
                    html_content.append(block.value.source)
                elif isinstance(block.value, str):
                    # Simple text block - wrap in paragraph
                    html_content.append(f'<p>{block.value}</p>')
        return ''.join(html_content)
    
    def get_word_count(self, obj):
        """Calculate word count from body text"""
        body_text = self.get_body_text(obj)
        return len(body_text.split()) if body_text else 0
    
    def get_related_posts(self, obj):
        """Get related posts based on categories"""
        related = BlogPage.objects.live().public().exclude(id=obj.id).filter(is_draft=False)
        
        if obj.categories.exists():
            related = related.filter(categories__in=obj.categories.all()).distinct()
        
        # Limit to 3 related posts
        related_posts = related[:3]
        
        return BlogPageSerializer(
            related_posts, 
            many=True, 
            context=self.context
        ).data


class AIModelSerializer(serializers.ModelSerializer):
    """
    Serializer for AI models
    """
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'provider', 'model_id', 'model_type', 
            'description', 'max_tokens', 'temperature', 'top_p',
            'is_active', 'rate_limit', 'created_at', 'updated_at'
        ]


class AIRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for AI requests
    """
    ai_model = AIModelSerializer(read_only=True)
    user_name = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = AIRequest
        fields = [
            'id', 'user_name', 'ai_model', 'request_type', 'input_text',
            'output_text', 'processing_time', 'tokens_used', 'cost',
            'status', 'created_at', 'completed_at', 'duration',
            'error_message'
        ]
        read_only_fields = [
            'user', 'processing_time', 'tokens_used', 'cost', 
            'status', 'completed_at', 'error_message'
        ]
    
    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    
    def get_duration(self, obj):
        """Get duration in human readable format"""
        if obj.processing_time:
            if obj.processing_time < 1:
                return f"{obj.processing_time * 1000:.0f}ms"
            else:
                return f"{obj.processing_time:.1f}s"
        return None


class ContactMessageSerializer(serializers.Serializer):
    """
    Serializer for contact form messages
    """
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    
    def validate_name(self, value):
        """Validate name field"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters long.")
        return value.strip()
    
    def validate_message(self, value):
        """Validate message field"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value.strip()


class StatsSerializer(serializers.Serializer):
    """
    Serializer for statistics data
    """
    total_posts = serializers.IntegerField()
    total_views = serializers.IntegerField()
    categories_count = serializers.IntegerField()
    authors_count = serializers.IntegerField()
    avg_reading_time = serializers.FloatField()
    popular_posts = BlogPageSerializer(many=True, read_only=True)
    recent_posts = BlogPageSerializer(many=True, read_only=True)


class SearchResultSerializer(serializers.Serializer):
    """
    Serializer for search results
    """
    query = serializers.CharField()
    total_results = serializers.IntegerField()
    blog_posts = BlogPageSerializer(many=True, read_only=True)
    
    
class ExportSerializer(serializers.Serializer):
    """
    Serializer for export requests
    """
    format = serializers.ChoiceField(choices=['json', 'csv'], default='json')
    include_drafts = serializers.BooleanField(default=False)
    date_from = serializers.DateField(required=False)
    date_to = serializers.DateField(required=False)


class AnalyticsSerializer(serializers.Serializer):
    """
    Serializer for analytics data
    """
    total_posts = serializers.IntegerField()
    total_views = serializers.IntegerField()
    avg_reading_time = serializers.FloatField()
    top_categories = serializers.ListField()
    monthly_posts = serializers.ListField()
    most_viewed_posts = BlogPageSerializer(many=True, read_only=True)


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for health check response
    """
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()
    database = serializers.CharField()
    blog_posts = serializers.IntegerField()
    services = serializers.DictField()


class VersionInfoSerializer(serializers.Serializer):
    """
    Serializer for version information
    """
    api_version = serializers.CharField()
    django_version = serializers.CharField()
    wagtail_version = serializers.CharField()
    last_updated = serializers.CharField()
    endpoints = serializers.DictField()
    features = serializers.ListField()
    supported_formats = serializers.ListField()