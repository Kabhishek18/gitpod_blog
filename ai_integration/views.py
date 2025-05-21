from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import json
import time

from .models import (
    AIModel, AIRequest, PromptTemplate, UserAIUsage, 
    AIFeedback, ContentAnalysis, AIGeneratedImage
)
from .services import (
    AIRequestProcessor, PromptManager, get_available_models, 
    check_user_quota, AIServiceError
)


class BaseAIView(APIView):
    """
    Base view for AI-related API endpoints
    """
    permission_classes = [IsAuthenticated]
    
    def dispatch(self, request, *args, **kwargs):
        # Check user quota before processing
        if request.user.is_authenticated:
            quota_info = check_user_quota(request.user)
            if not quota_info['has_quota']:
                return Response({
                    'error': 'AI usage quota exceeded',
                    'quota_info': quota_info
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        return super().dispatch(request, *args, **kwargs)


class GenerateBlogDraftView(BaseAIView):
    """
    Generate blog draft using AI
    """
    def post(self, request):
        data = request.data
        topic = data.get('topic', '')
        tone = data.get('tone', 'professional')
        length = data.get('length', 'medium')
        keywords = data.get('keywords', '')
        audience = data.get('audience', 'general')
        
        if not topic:
            return Response({
                'error': 'Topic is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create prompt using template
            prompt = PromptManager.render_prompt(
                'blog_draft',
                topic=topic,
                tone=tone,
                length=length,
                keywords=keywords,
                audience=audience
            )
            
            # Process AI request
            processor = AIRequestProcessor(request.user, 'blog_draft')
            result = processor.process_request(
                input_text=prompt,
                topic=topic,
                tone=tone,
                length=length
            )
            
            return Response({
                'draft': result['output'],
                'request_id': result['request_id'],
                'processing_time': result['processing_time'],
                'suggestions': {
                    'title_suggestions': self._generate_title_suggestions(topic),
                    'tag_suggestions': self._extract_tag_suggestions(result['output'])
                }
            })
            
        except AIServiceError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_title_suggestions(self, topic):
        """Generate title suggestions based on topic"""
        # Mock implementation - in real app, use AI
        return [
            f"Complete Guide to {topic}",
            f"Understanding {topic}: A Beginner's Guide",
            f"10 Things You Need to Know About {topic}",
            f"The Future of {topic}: Trends and Insights"
        ]
    
    def _extract_tag_suggestions(self, content):
        """Extract tag suggestions from content"""
        # Mock implementation - in real app, use AI
        common_tags = ['tutorial', 'guide', 'tips', 'development', 'programming']
        return common_tags[:3]


class ImproveBlogContentView(BaseAIView):
    """
    Improve existing blog content
    """
    def post(self, request):
        data = request.data
        content = data.get('content', '')
        improvement_type = data.get('type', 'readability')
        target_audience = data.get('audience', 'general')
        
        if not content:
            return Response({
                'error': 'Content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create prompt for content improvement
            prompt = PromptManager.render_prompt(
                'blog_improve',
                content=content,
                improvement_focus=improvement_type,
                audience=target_audience
            )
            
            processor = AIRequestProcessor(request.user, 'blog_improve')
            result = processor.process_request(
                input_text=prompt,
                improvement_type=improvement_type
            )
            
            return Response({
                'improved_content': result['output'],
                'request_id': result['request_id'],
                'improvements_made': self._analyze_improvements(content, result['output']),
                'readability_score': self._calculate_readability_score(result['output'])
            })
            
        except AIServiceError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _analyze_improvements(self, original, improved):
        """Analyze what improvements were made"""
        return {
            'word_count_change': len(improved.split()) - len(original.split()),
            'improvements': ['Better readability', 'Improved flow', 'Enhanced clarity']
        }
    
    def _calculate_readability_score(self, content):
        """Calculate readability score"""
        # Mock implementation
        return 85.5


class GenerateBlogTitleView(BaseAIView):
    """
    Generate blog titles using AI
    """
    def post(self, request):
        data = request.data
        topic = data.get('topic', '')
        keywords = data.get('keywords', '')
        tone = data.get('tone', 'professional')
        content_type = data.get('content_type', 'article')
        
        if not topic:
            return Response({
                'error': 'Topic is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            prompt = PromptManager.render_prompt(
                'title_generation',
                topic=topic,
                keywords=keywords,
                tone=tone,
                content_type=content_type
            )
            
            processor = AIRequestProcessor(request.user, 'title_generation')
            result = processor.process_request(input_text=prompt)
            
            # Parse titles from result
            titles = self._parse_titles(result['output'])
            
            return Response({
                'titles': titles,
                'request_id': result['request_id'],
                'seo_analysis': self._analyze_titles_seo(titles, keywords)
            })
            
        except AIServiceError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _parse_titles(self, output):
        """Parse titles from AI output"""
        lines = output.strip().split('\n')
        titles = []
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '-', '*')) or len(titles) < 8):
                # Clean up the title
                title = line.lstrip('123456789.-* ').strip()
                if title:
                    titles.append(title)
        return titles[:8]
    
    def _analyze_titles_seo(self, titles, keywords):
        """Analyze titles for SEO"""
        analysis = []
        for title in titles:
            analysis.append({
                'title': title,
                'length': len(title),
                'seo_score': 95 if len(title) <= 60 else 75,
                'has_keywords': bool(keywords and keywords.lower() in title.lower())
            })
        return analysis


class GenerateBlogTagsView(BaseAIView):
    """
    Generate blog tags using AI
    """
    def post(self, request):
        data = request.data
        content = data.get('content', '')
        title = data.get('title', '')
        category = data.get('category', '')
        
        if not content and not title:
            return Response({
                'error': 'Content or title is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Simple tag extraction for now
            tags = self._extract_tags(content, title, category)
            
            return Response({
                'suggested_tags': tags,
                'confidence_scores': {tag: 0.9 for tag in tags}
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _extract_tags(self, content, title, category):
        """Extract relevant tags from content"""
        # Mock implementation - in real app, use AI/NLP
        all_text = f"{title} {content} {category}".lower()
        
        potential_tags = [
            'python', 'django', 'javascript', 'react', 'ai', 'machine-learning',
            'web-development', 'tutorial', 'guide', 'tips', 'best-practices',
            'programming', 'coding', 'development', 'software', 'technology'
        ]
        
        relevant_tags = [tag for tag in potential_tags if tag in all_text]
        return relevant_tags[:8]


class OptimizeBlogSEOView(BaseAIView):
    """
    Optimize blog content for SEO
    """
    def post(self, request):
        data = request.data
        title = data.get('title', '')
        content = data.get('content', '')
        target_keyword = data.get('keyword', '')
        
        if not content:
            return Response({
                'error': 'Content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Generate SEO optimizations
            optimizations = self._generate_seo_optimizations(title, content, target_keyword)
            
            return Response({
                'seo_optimizations': optimizations,
                'current_seo_score': self._calculate_seo_score(title, content, target_keyword),
                'recommendations': self._get_seo_recommendations(title, content, target_keyword)
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_seo_optimizations(self, title, content, keyword):
        """Generate SEO optimizations"""
        return {
            'meta_description': f"Learn about {keyword} in this comprehensive guide. Discover key insights and practical tips.",
            'suggested_title': f"{title} - Complete {keyword} Guide",
            'keywords': [keyword, f"{keyword} tutorial", f"{keyword} guide"],
            'internal_links': ['Related tutorials', 'Best practices guide'],
            'image_alt_texts': [f"{keyword} diagram", f"{keyword} example"]
        }
    
    def _calculate_seo_score(self, title, content, keyword):
        """Calculate current SEO score"""
        score = 70  # Base score
        
        if keyword and keyword.lower() in title.lower():
            score += 10
        if keyword and keyword.lower() in content.lower():
            score += 10
        if len(title) <= 60:
            score += 5
        
        return min(score, 100)
    
    def _get_seo_recommendations(self, title, content, keyword):
        """Get SEO recommendations"""
        recommendations = []
        
        if not keyword:
            recommendations.append("Add a target keyword for better optimization")
        if len(title) > 60:
            recommendations.append("Shorten title to under 60 characters")
        if len(content.split()) < 300:
            recommendations.append("Add more content for better SEO (aim for 300+ words)")
        
        return recommendations


class AnalyzeBlogToneView(BaseAIView):
    """
    Analyze blog content tone
    """
    def post(self, request):
        data = request.data
        content = data.get('content', '')
        
        if not content:
            return Response({
                'error': 'Content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            processor = AIRequestProcessor(request.user, 'sentiment_analysis')
            result = processor.process_request(input_text=content)
            
            # Parse sentiment result
            tone_analysis = json.loads(result['output'])
            
            return Response({
                'tone': {
                    'primary_tone': tone_analysis.get('sentiment', 'NEUTRAL'),
                    'confidence': tone_analysis.get('confidence', 0.5),
                    'tone_score': self._calculate_tone_score(content),
                    'readability': self._calculate_readability_score(content)
                },
                'suggestions': self._get_tone_suggestions(tone_analysis.get('sentiment', 'NEUTRAL'))
            })
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_tone_score(self, content):
        """Calculate tone consistency score"""
        return 82.5  # Mock score
    
    def _get_tone_suggestions(self, sentiment):
        """Get tone improvement suggestions"""
        suggestions = {
            'POSITIVE': ['Great tone! Consider adding more specific examples.'],
            'NEGATIVE': ['Consider balancing with more positive language.'],
            'NEUTRAL': ['Consider adding more engaging language to make content more compelling.']
        }
        return suggestions.get(sentiment, suggestions['NEUTRAL'])


class AIModelListView(ListView):
    """
    List available AI models
    """
    model = AIModel
    template_name = 'ai_integration/model_list.html'
    context_object_name = 'models'
    
    def get_queryset(self):
        return AIModel.objects.filter(is_active=True)
    
    def get(self, request, *args, **kwargs):
        if request.content_type == 'application/json':
            models = get_available_models()
            return JsonResponse({'models': models})
        return super().get(request, *args, **kwargs)


class AIModelDetailView(DetailView):
    """
    AI model detail view
    """
    model = AIModel
    template_name = 'ai_integration/model_detail.html'
    context_object_name = 'model'
    
    def get(self, request, *args, **kwargs):
        if request.content_type == 'application/json':
            model = self.get_object()
            return JsonResponse({
                'id': model.id,
                'name': model.name,
                'provider': model.provider,
                'model_type': model.model_type,
                'description': model.description,
                'parameters': {
                    'max_tokens': model.max_tokens,
                    'temperature': model.temperature,
                    'top_p': model.top_p
                },
                'rate_limit': model.rate_limit,
                'is_active': model.is_active
            })
        return super().get(request, *args, **kwargs)


class AIUsageView(APIView):
    """
    Get AI usage statistics for current user
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        quota_info = check_user_quota(request.user)
        
        # Get recent requests
        recent_requests = AIRequest.objects.filter(
            user=request.user
        ).order_by('-created_at')[:10]
        
        request_data = []
        for req in recent_requests:
            request_data.append({
                'id': req.id,
                'type': req.request_type,
                'status': req.status,
                'created_at': req.created_at,
                'processing_time': req.processing_time,
                'tokens_used': req.tokens_used
            })
        
        return Response({
            'quota': quota_info,
            'recent_requests': request_data,
            'total_requests': AIRequest.objects.filter(user=request.user).count()
        })


class AIAnalyticsView(APIView):
    """
    AI analytics for administrators
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_staff:
            return Response({
                'error': 'Admin access required'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate analytics
        total_requests = AIRequest.objects.count()
        successful_requests = AIRequest.objects.filter(status='completed').count()
        
        # Most used models
        from django.db.models import Count
        popular_models = AIModel.objects.annotate(
            request_count=Count('requests')
        ).order_by('-request_count')[:5]
        
        return Response({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'success_rate': (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            'popular_models': [
                {
                    'name': model.name,
                    'request_count': model.request_count
                } for model in popular_models
            ]
        })


# Additional view classes that need to be implemented
class AnalyzeReadabilityView(BaseAIView):
    def post(self, request):
        # Implementation for readability analysis
        pass

class AnalyzeSentimentView(BaseAIView):
    def post(self, request):
        # Implementation for sentiment analysis
        pass

class ExtractKeywordsView(BaseAIView):
    def post(self, request):
        # Implementation for keyword extraction
        pass

class AnalyzeContentView(BaseAIView):
    def post(self, request):
        # Implementation for content analysis
        pass

class ExpandTextView(BaseAIView):
    def post(self, request):
        # Implementation for text expansion
        pass

class SummarizeTextView(BaseAIView):
    def post(self, request):
        # Implementation for text summarization
        pass

class GrammarCheckView(BaseAIView):
    def post(self, request):
        # Implementation for grammar checking
        pass

class AdjustToneView(BaseAIView):
    def post(self, request):
        # Implementation for tone adjustment
        pass

class TranslateTextView(BaseAIView):
    def post(self, request):
        # Implementation for text translation
        pass

class GenerateImageView(BaseAIView):
    def post(self, request):
        # Implementation for image generation
        pass

class AIImageGalleryView(ListView):
    def get(self, request):
        # Implementation for image gallery
        pass

class AIImageDetailView(DetailView):
    def get(self, request, pk):
        # Implementation for image detail
        pass

class GenerateMetaDescriptionView(BaseAIView):
    def post(self, request):
        # Implementation for meta description generation
        pass

class SuggestKeywordsView(BaseAIView):
    def post(self, request):
        # Implementation for keyword suggestions
        pass

class OptimizeContentView(BaseAIView):
    def post(self, request):
        # Implementation for content optimization
        pass

class TestAIModelView(BaseAIView):
    def post(self, request):
        # Implementation for AI model testing
        pass

class PromptTemplateListView(ListView):
    def get(self, request):
        # Implementation for prompt template list
        pass

class PromptTemplateDetailView(DetailView):
    def get(self, request, pk):
        # Implementation for prompt template detail
        pass

class RenderPromptTemplateView(BaseAIView):
    def post(self, request):
        # Implementation for prompt template rendering
        pass

class AIFeedbackView(BaseAIView):
    def post(self, request):
        # Implementation for AI feedback
        pass

class SuggestProjectDescriptionView(BaseAIView):
    def post(self, request):
        # Implementation for project description suggestions
        pass

class SuggestPortfolioContentView(BaseAIView):
    def post(self, request):
        # Implementation for portfolio content suggestions
        pass

class SuggestSkillsView(BaseAIView):
    def post(self, request):
        # Implementation for skills suggestions
        pass

class BatchAnalyzeView(BaseAIView):
    def post(self, request):
        # Implementation for batch analysis
        pass

class BatchOptimizeView(BaseAIView):
    def post(self, request):
        # Implementation for batch optimization
        pass

class AIProcessingWebhookView(View):
    def post(self, request):
        # Implementation for AI processing webhook
        pass

class AIChatView(BaseAIView):
    def post(self, request):
        # Implementation for AI chat
        pass

class AIChatHistoryView(BaseAIView):
    def get(self, request):
        # Implementation for AI chat history
        pass