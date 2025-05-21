from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'blog', views.BlogPostViewSet, basename='blogpost')
router.register(r'blog-categories', views.BlogCategoryViewSet, basename='blogcategory')
router.register(r'blog-authors', views.BlogAuthorViewSet, basename='blogauthor')
router.register(r'ai-models', views.AIModelViewSet, basename='aimodel')
router.register(r'ai-requests', views.AIRequestViewSet, basename='airequest')

# Placeholder viewsets (for portfolio app endpoints that don't exist)
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'skills', views.SkillViewSet, basename='skill')
router.register(r'technologies', views.TechnologyViewSet, basename='technology')
router.register(r'experiences', views.ExperienceViewSet, basename='experience')
router.register(r'education', views.EducationViewSet, basename='education')

app_name = 'api'

urlpatterns = [
    # API root
    path('', include(router.urls)),
    
    # Authentication
    path('auth/', include('rest_framework.urls')),
    
    # Stats endpoints
    path('portfolio/stats/', views.PortfolioStatsView.as_view(), name='portfolio-stats'),
    path('blog/stats/', views.BlogStatsView.as_view(), name='blog-stats'),
    
    # Contact
    path('contact/', views.ContactView.as_view(), name='contact'),
    
    # Resume
    path('resume/download/', views.ResumeDownloadView.as_view(), name='resume-download'),
    
    # Search endpoints
    path('search/', views.SearchView.as_view(), name='search'),
    path('search/projects/', views.ProjectSearchView.as_view(), name='project-search'),
    path('search/blog/', views.BlogSearchView.as_view(), name='blog-search'),
    
    # Analytics endpoints
    path('analytics/projects/', views.ProjectAnalyticsView.as_view(), name='project-analytics'),
    path('analytics/blog/', views.BlogAnalyticsView.as_view(), name='blog-analytics'),
    
    # Export endpoints
    path('export/projects/', views.ProjectExportView.as_view(), name='project-export'),
    path('export/blog/', views.BlogExportView.as_view(), name='blog-export'),
    path('export/portfolio/', views.PortfolioExportView.as_view(), name='portfolio-export'),
    
    # Webhook endpoints
    path('webhooks/', views.WebhookListView.as_view(), name='webhook-list'),
    path('webhooks/<int:pk>/', views.WebhookDetailView.as_view(), name='webhook-detail'),
    
    # Health check
    path('health/', views.HealthCheckView.as_view(), name='health-check'),
    
    # Version info
    path('version/', views.VersionInfoView.as_view(), name='version-info'),
    
    # Simple docs endpoint instead of fancy documentation
    path('docs/', views.ApiDocsView.as_view(), name='api-docs'),
]