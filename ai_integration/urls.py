from django.urls import path
from . import views

app_name = 'ai_integration'

urlpatterns = [
    # Blog AI assistance
    path('blog/generate-draft/', views.GenerateBlogDraftView.as_view(), name='generate-blog-draft'),
    path('blog/improve-content/', views.ImproveBlogContentView.as_view(), name='improve-blog-content'),
    path('blog/generate-title/', views.GenerateBlogTitleView.as_view(), name='generate-blog-title'),
    path('blog/generate-tags/', views.GenerateBlogTagsView.as_view(), name='generate-blog-tags'),
    path('blog/seo-optimize/', views.OptimizeBlogSEOView.as_view(), name='optimize-blog-seo'),
    path('blog/analyze-tone/', views.AnalyzeBlogToneView.as_view(), name='analyze-blog-tone'),
    
    # Content analysis
    path('analyze/readability/', views.AnalyzeReadabilityView.as_view(), name='analyze-readability'),
    path('analyze/sentiment/', views.AnalyzeSentimentView.as_view(), name='analyze-sentiment'),
    path('analyze/keywords/', views.ExtractKeywordsView.as_view(), name='extract-keywords'),
    path('analyze/content/', views.AnalyzeContentView.as_view(), name='analyze-content'),
    
    # Text operations
    path('text/expand/', views.ExpandTextView.as_view(), name='expand-text'),
    path('text/summarize/', views.SummarizeTextView.as_view(), name='summarize-text'),
    path('text/grammar-check/', views.GrammarCheckView.as_view(), name='grammar-check'),
    path('text/tone-adjust/', views.AdjustToneView.as_view(), name='adjust-tone'),
    path('text/translate/', views.TranslateTextView.as_view(), name='translate-text'),
    
    # Image generation
    path('image/generate/', views.GenerateImageView.as_view(), name='generate-image'),
    path('image/gallery/', views.AIImageGalleryView.as_view(), name='ai-image-gallery'),
    path('image/<int:pk>/', views.AIImageDetailView.as_view(), name='ai-image-detail'),
    
    # SEO assistance
    path('seo/meta-description/', views.GenerateMetaDescriptionView.as_view(), name='generate-meta-description'),
    path('seo/keywords/', views.SuggestKeywordsView.as_view(), name='suggest-keywords'),
    path('seo/optimize/', views.OptimizeContentView.as_view(), name='optimize-content'),
    
    # AI models management
    path('models/', views.AIModelListView.as_view(), name='ai-model-list'),
    path('models/<int:pk>/', views.AIModelDetailView.as_view(), name='ai-model-detail'),
    path('models/test/', views.TestAIModelView.as_view(), name='test-ai-model'),
    
    # Prompt templates
    path('templates/', views.PromptTemplateListView.as_view(), name='prompt-template-list'),
    path('templates/<int:pk>/', views.PromptTemplateDetailView.as_view(), name='prompt-template-detail'),
    path('templates/render/', views.RenderPromptTemplateView.as_view(), name='render-prompt-template'),
    
    # Usage and analytics
    path('usage/', views.AIUsageView.as_view(), name='ai-usage'),
    path('analytics/', views.AIAnalyticsView.as_view(), name='ai-analytics'),
    path('feedback/', views.AIFeedbackView.as_view(), name='ai-feedback'),
    
    # Content suggestions
    path('suggest/project-description/', views.SuggestProjectDescriptionView.as_view(), name='suggest-project-description'),
    path('suggest/portfolio-content/', views.SuggestPortfolioContentView.as_view(), name='suggest-portfolio-content'),
    path('suggest/skills/', views.SuggestSkillsView.as_view(), name='suggest-skills'),
    
    # Batch operations
    path('batch/analyze/', views.BatchAnalyzeView.as_view(), name='batch-analyze'),
    path('batch/optimize/', views.BatchOptimizeView.as_view(), name='batch-optimize'),
    
    # Webhook for AI processing
    path('webhook/process/', views.AIProcessingWebhookView.as_view(), name='ai-processing-webhook'),
    
    # AI assistant chat interface
    path('chat/', views.AIChatView.as_view(), name='ai-chat'),
    path('chat/history/', views.AIChatHistoryView.as_view(), name='ai-chat-history'),
]