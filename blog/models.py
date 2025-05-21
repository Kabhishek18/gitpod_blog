from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail import blocks
from wagtail.snippets.models import register_snippet
from wagtail.search import index
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager


@register_snippet
class BlogCategory(models.Model):
    """
    Blog category snippet
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#0066cc', help_text="Hex color code")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']


class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'BlogPage',
        related_name='tagged_items',
        on_delete=models.CASCADE
    )


class BlogPage(Page):
    """
    Individual blog post page
    """
    # Basic fields
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    
    publish_date = models.DateTimeField(default=timezone.now)
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_featured_image'
    )
    
    # Content
    excerpt = models.TextField(
        max_length=300,
        help_text="Brief description of the blog post"
    )
    
    # Blog content using StreamField for flexibility
    body = StreamField([
        ('heading', blocks.CharBlock(form_classname="title")),
        ('paragraph', blocks.RichTextBlock()),
        ('image', blocks.ImageChooserBlock()),
        ('code', blocks.TextBlock(help_text="Code snippet")),
        ('quote', blocks.BlockQuoteBlock()),
        ('gallery', blocks.StreamBlock([
            ('image', blocks.ImageChooserBlock()),
        ])),
        ('embed', blocks.RawHTMLBlock()),
        ('table', blocks.TextBlock(help_text="HTML table")),
    ], use_json_field=True)
    
    # Categories and tags
    categories = ParentalManyToManyField(BlogCategory, blank=True)
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    
    # SEO and metadata
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="SEO meta description"
    )
    
    # Reading metrics
    reading_time = models.PositiveIntegerField(
        default=0,
        help_text="Estimated reading time in minutes"
    )
    view_count = models.PositiveIntegerField(default=0)
    
    # AI-enhanced fields
    ai_generated_summary = models.TextField(
        blank=True,
        help_text="AI-generated summary of the blog post"
    )
    ai_suggested_tags = models.TextField(
        blank=True,
        help_text="AI-suggested tags (comma-separated)"
    )
    ai_seo_keywords = models.TextField(
        blank=True,
        help_text="AI-suggested SEO keywords"
    )
    ai_content_score = models.FloatField(
        null=True,
        blank=True,
        help_text="AI content quality score (0-1)"
    )
    tone_analysis = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('professional', 'Professional'),
            ('casual', 'Casual'),
            ('technical', 'Technical'),
            ('creative', 'Creative'),
            ('educational', 'Educational'),
        ],
        help_text="AI-detected tone of the content"
    )
    
    # Draft management
    is_draft = models.BooleanField(default=True)
    draft_notes = models.TextField(blank=True, help_text="Internal notes for drafts")
    
    # Social sharing
    social_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='blog_social_image',
        help_text="Image for social media sharing (defaults to featured image)"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('author'),
            FieldPanel('publish_date'),
            FieldPanel('is_draft'),
        ], heading="Publishing"),
        
        MultiFieldPanel([
            FieldPanel('featured_image'),
            FieldPanel('social_image'),
        ], heading="Images"),
        
        FieldPanel('excerpt'),
        FieldPanel('body'),
        
        MultiFieldPanel([
            FieldPanel('categories'),
            FieldPanel('tags'),
        ], heading="Categories & Tags"),
        
        MultiFieldPanel([
            FieldPanel('meta_description'),
            FieldPanel('reading_time'),
        ], heading="SEO & Metadata"),
        
        MultiFieldPanel([
            FieldPanel('ai_generated_summary'),
            FieldPanel('ai_suggested_tags'),
            FieldPanel('ai_seo_keywords'),
            FieldPanel('ai_content_score'),
            FieldPanel('tone_analysis'),
        ], heading="AI Enhancements"),
        
        FieldPanel('draft_notes'),
    ]

    search_fields = Page.search_fields + [
        index.SearchField('excerpt'),
        index.SearchField('body'),
        index.FilterField('publish_date'),
        index.FilterField('author'),
    ]

    def save(self, *args, **kwargs):
        # Calculate reading time based on word count
        if self.body:
            word_count = sum(len(str(block.value).split()) for block in self.body)
            self.reading_time = max(1, word_count // 200)  # Assuming 200 words per minute
        
        super().save(*args, **kwargs)

    def get_context(self, request):
        context = super().get_context(request)
        
        # Increment view count
        self.view_count += 1
        self.save(update_fields=['view_count'])
        
        # Get related posts
        related_posts = BlogPage.objects.live().public().exclude(id=self.id)
        
        # Filter by same categories
        if self.categories.exists():
            related_posts = related_posts.filter(categories__in=self.categories.all())
        
        context['related_posts'] = related_posts.distinct()[:3]
        context['recent_posts'] = BlogPage.objects.live().public()[:5]
        
        return context

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"


class BlogIndexPage(Page):
    """
    Blog listing page
    """
    intro = RichTextField(blank=True)
    featured_post = models.ForeignKey(
        BlogPage,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='featured_in_index'
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('featured_post'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        
        # Get all published blog posts
        blog_posts = BlogPage.objects.live().public().filter(is_draft=False)
        
        # Filter by category if specified
        category = request.GET.get('category')
        if category:
            blog_posts = blog_posts.filter(categories__slug=category)
        
        # Filter by tag if specified
        tag = request.GET.get('tag')
        if tag:
            blog_posts = blog_posts.filter(tags__name__icontains=tag)
        
        # Search functionality
        search_query = request.GET.get('search')
        if search_query:
            blog_posts = blog_posts.search(search_query)
        
        # Ordering
        order_by = request.GET.get('order', '-publish_date')
        if order_by in ['-publish_date', 'publish_date', '-view_count', 'title']:
            blog_posts = blog_posts.order_by(order_by)
        else:
            blog_posts = blog_posts.order_by('-publish_date')
        
        # Pagination
        from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
        paginator = Paginator(blog_posts, 10)  # Show 10 posts per page
        page = request.GET.get('page')
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        
        context['blog_posts'] = posts
        context['categories'] = BlogCategory.objects.all()
        context['popular_posts'] = BlogPage.objects.live().public().filter(
            is_draft=False
        ).order_by('-view_count')[:5]
        context['recent_posts'] = BlogPage.objects.live().public().filter(
            is_draft=False
        ).order_by('-publish_date')[:5]
        
        return context


@register_snippet
class BlogAuthor(models.Model):
    """
    Extended author profile for blog posts
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = RichTextField(blank=True)
    avatar = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='author_avatar'
    )
    
    # Social links
    website = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    
    # Author stats
    posts_count = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def update_stats(self):
        """Update author statistics"""
        posts = BlogPage.objects.filter(author=self.user, is_draft=False)
        self.posts_count = posts.count()
        self.total_views = sum(post.view_count for post in posts)
        self.save()

    class Meta:
        verbose_name = "Blog Author"
        verbose_name_plural = "Blog Authors"


class AIBlogAssistant(models.Model):
    """
    Model to track AI assistance requests and results
    """
    blog_post = models.ForeignKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name='ai_assistance_records'
    )
    
    assistance_type = models.CharField(max_length=50, choices=[
        ('draft_suggestion', 'Draft Suggestion'),
        ('expand_paragraph', 'Expand Paragraph'),
        ('shorten_content', 'Shorten Content'),
        ('grammar_fix', 'Grammar Fix'),
        ('tone_adjustment', 'Tone Adjustment'),
        ('seo_optimization', 'SEO Optimization'),
        ('tag_suggestion', 'Tag Suggestion'),
        ('title_generation', 'Title Generation'),
        ('meta_description', 'Meta Description'),
    ])
    
    input_text = models.TextField(help_text="Original text or prompt")
    output_text = models.TextField(help_text="AI-generated result")
    
    # AI model information
    model_used = models.CharField(max_length=100, blank=True)
    processing_time = models.FloatField(null=True, blank=True, help_text="Time in seconds")
    
    # Feedback
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(i, i) for i in range(1, 6)],
        help_text="User rating 1-5"
    )
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    applied = models.BooleanField(default=False, help_text="Whether the AI suggestion was applied")

    def __str__(self):
        return f"{self.assistance_type} for {self.blog_post.title}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "AI Blog Assistant Record"
        verbose_name_plural = "AI Blog Assistant Records"


class BlogSeries(models.Model):
    """
    Model for blog post series
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    
    cover_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='series_cover'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title

    def get_posts(self):
        """Get all posts in this series, ordered by series order"""
        return self.posts.filter(is_draft=False).order_by('series_order')

    def get_post_count(self):
        """Get total number of posts in series"""
        return self.posts.filter(is_draft=False).count()

    class Meta:
        verbose_name_plural = "Blog Series"
        ordering = ['-created_at']


class BlogSeriesPost(models.Model):
    """
    Through model for blog posts in series
    """
    blog_post = models.ForeignKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name='in_series'
    )
    series = models.ForeignKey(
        BlogSeries,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    series_order = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ['blog_post', 'series']
        ordering = ['series_order']


class BlogComment(models.Model):
    """
    Comments model for blog posts
    """
    blog_post = models.ForeignKey(
        BlogPage,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    # Comment details
    author_name = models.CharField(max_length=100)
    author_email = models.EmailField()
    author_website = models.URLField(blank=True)
    
    content = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)
    
    # Threading for replies
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author_name} on {self.blog_post.title}"

    def get_replies(self):
        """Get approved replies to this comment"""
        return self.replies.filter(is_approved=True, is_spam=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Blog Comment"
        verbose_name_plural = "Blog Comments"


class BlogAnalytics(models.Model):
    """
    Analytics model for tracking blog performance
    """
    blog_post = models.OneToOneField(
        BlogPage,
        on_delete=models.CASCADE,
        related_name='analytics'
    )
    
    # View analytics
    total_views = models.PositiveIntegerField(default=0)
    unique_views = models.PositiveIntegerField(default=0)
    avg_time_on_page = models.FloatField(default=0.0, help_text="Average time in seconds")
    bounce_rate = models.FloatField(default=0.0, help_text="Bounce rate percentage")
    
    # Engagement analytics
    total_comments = models.PositiveIntegerField(default=0)
    total_shares = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    
    # SEO analytics
    search_impressions = models.PositiveIntegerField(default=0)
    search_clicks = models.PositiveIntegerField(default=0)
    avg_position = models.FloatField(default=0.0, help_text="Average search position")
    
    # Traffic sources
    direct_traffic = models.PositiveIntegerField(default=0)
    search_traffic = models.PositiveIntegerField(default=0)
    social_traffic = models.PositiveIntegerField(default=0)
    referral_traffic = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)

    def calculate_ctr(self):
        """Calculate click-through rate from search"""
        if self.search_impressions > 0:
            return (self.search_clicks / self.search_impressions) * 100
        return 0

    def __str__(self):
        return f"Analytics for {self.blog_post.title}"

    class Meta:
        verbose_name_plural = "Blog Analytics"