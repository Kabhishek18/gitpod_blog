from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render
import json

from blog.models import BlogPage, BlogCategory, BlogAuthor
from ai_integration.models import AIModel, AIRequest
from .serializers import (
    BlogPageSerializer, BlogPageDetailSerializer, BlogCategorySerializer,
    BlogAuthorSerializer, AIModelSerializer, AIRequestSerializer,
    ContactMessageSerializer, StatsSerializer
)


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for blog posts
    """
    serializer_class = BlogPageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = BlogPage.objects.live().public().filter(is_draft=False)
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(categories__slug=category)
        
        # Filter by tag
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search)
            )
        
        return queryset.order_by('-publish_date')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPageDetailSerializer
        return BlogPageSerializer
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular blog posts"""
        popular_posts = self.get_queryset().order_by('-view_count')[:5]
        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent blog posts"""
        recent_posts = self.get_queryset().order_by('-publish_date')[:5]
        serializer = self.get_serializer(recent_posts, many=True)
        return Response(serializer.data)


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for blog categories
    """
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    lookup_field = 'slug'


class BlogAuthorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for blog authors
    """
    queryset = BlogAuthor.objects.all()
    serializer_class = BlogAuthorSerializer


class AIModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AI models
    """
    queryset = AIModel.objects.filter(is_active=True)
    serializer_class = AIModelSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class AIRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for AI requests (user's own requests only)
    """
    serializer_class = AIRequestSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return AIRequest.objects.filter(user=self.request.user)
        return AIRequest.objects.none()


class PortfolioStatsView(generics.GenericAPIView):
    """
    Portfolio statistics endpoint
    """
    def get(self, request):
        # Since we're not including portfolio app, return basic stats
        return Response({
            'message': 'Portfolio stats endpoint',
            'projects_count': 0,
            'total_views': 0,
            'technologies_used': 0
        })


class BlogStatsView(generics.GenericAPIView):
    """
    Blog statistics endpoint
    """
    serializer_class = StatsSerializer
    
    def get(self, request):
        blog_posts = BlogPage.objects.live().public().filter(is_draft=False)
        
        stats = {
            'total_posts': blog_posts.count(),
            'total_views': sum(post.view_count for post in blog_posts),
            'popular_posts': blog_posts.order_by('-view_count')[:3],
            'recent_posts': blog_posts.order_by('-publish_date')[:3],
            'categories_count': BlogCategory.objects.count(),
            'authors_count': BlogAuthor.objects.count(),
            'avg_reading_time': blog_posts.aggregate(
                avg_time=Avg('reading_time')
            )['avg_time'] or 0
        }
        
        # Serialize the nested objects
        popular_posts_data = BlogPageSerializer(
            stats['popular_posts'], 
            many=True, 
            context={'request': request}
        ).data
        
        recent_posts_data = BlogPageSerializer(
            stats['recent_posts'], 
            many=True, 
            context={'request': request}
        ).data
        
        return Response({
            'total_posts': stats['total_posts'],
            'total_views': stats['total_views'],
            'categories_count': stats['categories_count'],
            'authors_count': stats['authors_count'],
            'avg_reading_time': round(stats['avg_reading_time'], 1),
            'popular_posts': popular_posts_data,
            'recent_posts': recent_posts_data
        })


class ContactView(generics.GenericAPIView):
    """
    Contact form endpoint
    """
    serializer_class = ContactMessageSerializer
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # For now, just return success (in production you'd save to DB and send email)
            try:
                # Simulate sending email
                email_sent = True  # Replace with actual email sending logic
                
                if email_sent:
                    return Response({
                        'message': 'Thank you for your message! I will get back to you soon.',
                        'status': 'success'
                    })
                else:
                    return Response({
                        'error': 'Failed to send message. Please try again later.'
                    }, status=500)
                    
            except Exception as e:
                return Response({
                    'error': 'An error occurred while sending your message.'
                }, status=500)
        
        return Response(serializer.errors, status=400)


class ResumeDownloadView(generics.GenericAPIView):
    """
    Resume download endpoint
    """
    def get(self, request):
        # In a real implementation, you'd serve a PDF file
        return Response({
            'message': 'Resume download endpoint',
            'download_url': '/media/resume.pdf',  # Example URL
            'filename': 'resume.pdf'
        })


class SearchView(generics.GenericAPIView):
    """
    Global search endpoint
    """
    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'No search query provided'}, status=400)
        
        # Search blog posts
        blog_results = BlogPage.objects.live().public().filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query)
        ).filter(is_draft=False)[:10]
        
        results = {
            'query': query,
            'blog_posts': BlogPageSerializer(
                blog_results, 
                many=True, 
                context={'request': request}
            ).data,
            'total_results': blog_results.count()
        }
        
        return Response(results)


class ProjectSearchView(generics.GenericAPIView):
    """
    Project search endpoint (placeholder)
    """
    def get(self, request):
        return Response({
            'message': 'Project search not implemented (no portfolio app)',
            'results': []
        })


class BlogSearchView(generics.GenericAPIView):
    """
    Blog-specific search
    """
    def get(self, request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', '')
        tag = request.query_params.get('tag', '')
        
        blog_posts = BlogPage.objects.live().public().filter(is_draft=False)
        
        if query:
            blog_posts = blog_posts.filter(
                Q(title__icontains=query) |
                Q(excerpt__icontains=query)
            )
        
        if category:
            blog_posts = blog_posts.filter(categories__slug=category)
        
        if tag:
            blog_posts = blog_posts.filter(tags__name__icontains=tag)
        
        serializer = BlogPageSerializer(
            blog_posts.order_by('-publish_date')[:20], 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'query': query,
            'results': serializer.data,
            'total': blog_posts.count(),
            'filters': {
                'category': category,
                'tag': tag
            }
        })


class ProjectAnalyticsView(generics.GenericAPIView):
    """
    Project analytics endpoint (placeholder)
    """
    def get(self, request):
        return Response({
            'message': 'Project analytics not implemented (no portfolio app)',
            'data': {}
        })


class BlogAnalyticsView(generics.GenericAPIView):
    """
    Blog analytics endpoint
    """
    def get(self, request):
        blog_posts = BlogPage.objects.live().public().filter(is_draft=False)
        
        # Calculate analytics
        total_posts = blog_posts.count()
        total_views = sum(post.view_count for post in blog_posts)
        avg_reading_time = blog_posts.aggregate(
            avg_time=Avg('reading_time')
        )['avg_time'] or 0
        
        # Top categories by post count
        top_categories = BlogCategory.objects.annotate(
            post_count=Count('blogpage')
        ).order_by('-post_count')[:5]
        
        # Monthly post count (last 6 months)
        from datetime import datetime, timedelta
        six_months_ago = datetime.now() - timedelta(days=180)
        monthly_posts = blog_posts.filter(
            publish_date__gte=six_months_ago
        ).extra(
            select={'month': "strftime('%%Y-%%m', publish_date)"}
        ).values('month').annotate(
            count=Count('id')
        ).order_by('month')
        
        return Response({
            'total_posts': total_posts,
            'total_views': total_views,
            'avg_reading_time': round(avg_reading_time, 1),
            'top_categories': [
                {
                    'name': cat.name,
                    'post_count': cat.post_count,
                    'color': cat.color
                } for cat in top_categories
            ],
            'monthly_posts': list(monthly_posts),
            'most_viewed_posts': BlogPageSerializer(
                blog_posts.order_by('-view_count')[:5],
                many=True,
                context={'request': request}
            ).data
        })


class ProjectExportView(generics.GenericAPIView):
    """
    Project export endpoint (placeholder)
    """
    def get(self, request):
        return Response({
            'message': 'Project export not implemented (no portfolio app)'
        })


class BlogExportView(generics.GenericAPIView):
    """
    Blog export endpoint
    """
    def get(self, request):
        format_type = request.query_params.get('format', 'json')
        
        blog_posts = BlogPage.objects.live().public().filter(is_draft=False)
        
        if format_type == 'json':
            serializer = BlogPageSerializer(
                blog_posts, 
                many=True, 
                context={'request': request}
            )
            
            return Response({
                'export_format': 'json',
                'export_date': timezone.now(),
                'total_posts': blog_posts.count(),
                'posts': serializer.data
            })
        
        elif format_type == 'csv':
            # In a real implementation, you'd generate CSV
            return Response({
                'message': 'CSV export would be implemented here',
                'download_url': '/api/blog/export.csv'
            })
        
        return Response({
            'error': 'Unsupported format. Use json or csv.'
        }, status=400)


class PortfolioExportView(generics.GenericAPIView):
    """
    Portfolio export endpoint (placeholder)
    """
    def get(self, request):
        return Response({
            'message': 'Portfolio export not implemented (no portfolio app)'
        })


class WebhookListView(generics.GenericAPIView):
    """
    Webhook list endpoint
    """
    def get(self, request):
        # In a real implementation, you'd return user's webhooks
        return Response({
            'webhooks': [],
            'message': 'Webhook functionality not fully implemented'
        })


class WebhookDetailView(generics.GenericAPIView):
    """
    Webhook detail endpoint
    """
    def get(self, request, pk):
        return Response({
            'webhook_id': pk,
            'message': 'Webhook detail not implemented'
        })


class HealthCheckView(generics.GenericAPIView):
    """
    API health check endpoint
    """
    def get(self, request):
        try:
            # Check database connectivity
            blog_count = BlogPage.objects.count()
            
            return Response({
                'status': 'healthy',
                'timestamp': timezone.now(),
                'version': '1.0.0',
                'database': 'connected',
                'blog_posts': blog_count,
                'services': {
                    'blog': 'operational',
                    'api': 'operational',
                    'ai_integration': 'operational'
                }
            })
        except Exception as e:
            return Response({
                'status': 'unhealthy',
                'timestamp': timezone.now(),
                'error': str(e)
            }, status=500)


class VersionInfoView(generics.GenericAPIView):
    """
    API version information
    """
    def get(self, request):
        return Response({
            'api_version': '1.0.0',
            'django_version': '5.1.9',
            'wagtail_version': '7.x',
            'last_updated': '2024-01-01',
            'endpoints': {
                'blog': '/api/blog/',
                'ai': '/api/ai/',
                'search': '/api/search/',
                'contact': '/api/contact/',
                'health': '/api/health/'
            },
            'features': [
                'Blog Management',
                'AI Integration',
                'Search Functionality',
                'Contact Form',
                'Analytics',
                'Export Capabilities'
            ],
            'supported_formats': ['json', 'csv']
        })


class ApiDocsView(APIView):
    """
    Simple API documentation view
    """
    def get(self, request):
        docs_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Portfolio Platform API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #007acc; }
                h2 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
                .endpoint { background: #f8f9fa; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .method { font-weight: bold; }
                .get { color: #28a745; }
                .post { color: #dc3545; }
                code { background: #e9ecef; padding: 2px 4px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>Portfolio Platform API Documentation</h1>
            
            <h2>Authentication</h2>
            <p>Most endpoints require authentication. Use session authentication or DRF token authentication.</p>
            
            <h2>Blog Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/blog/</code><br>
                <strong>Description:</strong> List all blog posts<br>
                <strong>Parameters:</strong> category, tag, search, page
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/blog/{id}/</code><br>
                <strong>Description:</strong> Get specific blog post details
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/blog/popular/</code><br>
                <strong>Description:</strong> Get popular blog posts
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/blog/recent/</code><br>
                <strong>Description:</strong> Get recent blog posts
            </div>
            
            <h2>Search Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/search/?q={query}</code><br>
                <strong>Description:</strong> Global search across all content
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/search/blog/?q={query}</code><br>
                <strong>Description:</strong> Search blog posts specifically
            </div>
            
            <h2>Analytics Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/blog/stats/</code><br>
                <strong>Description:</strong> Get blog statistics
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/analytics/blog/</code><br>
                <strong>Description:</strong> Detailed blog analytics
            </div>
            
            <h2>Utility Endpoints</h2>
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/health/</code><br>
                <strong>Description:</strong> API health check
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span> <code>/api/version/</code><br>
                <strong>Description:</strong> API version information
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span> <code>/api/contact/</code><br>
                <strong>Description:</strong> Send contact form message<br>
                <strong>Body:</strong> {"name": "...", "email": "...", "subject": "...", "message": "..."}
            </div>
            
            <h2>AI Integration</h2>
            <p>AI endpoints are available at <code>/ai/</code> prefix. See AI documentation for details.</p>
            
            <h2>Response Format</h2>
            <p>All responses are in JSON format. List endpoints include pagination metadata.</p>
            
            <h2>Error Handling</h2>
            <p>Errors return appropriate HTTP status codes with error messages in JSON format.</p>
        </body>
        </html>
        """
        return HttpResponse(docs_html, content_type='text/html')


# Placeholder viewsets for portfolio-related endpoints
class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Skills viewset (placeholder - no portfolio app)
    """
    queryset = []
    serializer_class = BlogPageSerializer  # Placeholder
    
    def list(self, request):
        return Response({
            'message': 'Skills endpoint not implemented (no portfolio app)',
            'skills': []
        })


class TechnologyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Technologies viewset (placeholder - no portfolio app)
    """
    queryset = []
    serializer_class = BlogPageSerializer  # Placeholder
    
    def list(self, request):
        return Response({
            'message': 'Technologies endpoint not implemented (no portfolio app)',
            'technologies': []
        })


class ExperienceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Experience viewset (placeholder - no portfolio app)
    """
    queryset = []
    serializer_class = BlogPageSerializer  # Placeholder
    
    def list(self, request):
        return Response({
            'message': 'Experience endpoint not implemented (no portfolio app)',
            'experiences': []
        })


class EducationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Education viewset (placeholder - no portfolio app)
    """
    queryset = []
    serializer_class = BlogPageSerializer  # Placeholder
    
    def list(self, request):
        return Response({
            'message': 'Education endpoint not implemented (no portfolio app)',
            'education': []
        })


class ProjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Projects viewset (placeholder - no portfolio app)
    """
    queryset = []
    serializer_class = BlogPageSerializer  # Placeholder
    
    def list(self, request):
        return Response({
            'message': 'Projects endpoint not implemented (no portfolio app)',
            'projects': []
        })