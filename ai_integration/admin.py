from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Avg, Sum
from django.utils import timezone
import json

from .models import (
    AIModel, AIRequest, PromptTemplate, UserAIUsage, 
    AIFeedback, ContentAnalysis, AIGeneratedImage
)


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    """
    Admin interface for AI models
    """
    list_display = [
        'name', 'provider', 'model_type', 'is_active', 
        'rate_limit', 'request_count', 'last_tested_display'
    ]
    list_filter = ['provider', 'model_type', 'is_active']
    search_fields = ['name', 'model_id', 'description']
    readonly_fields = ['last_tested', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'provider', 'model_id', 'model_type', 'description')
        }),
        ('Configuration', {
            'fields': ('max_tokens', 'temperature', 'top_p', 'api_endpoint', 'requires_auth')
        }),
        ('Rate Limiting', {
            'fields': ('rate_limit', 'is_active')
        }),
        ('Status', {
            'fields': ('last_tested', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['test_models', 'activate_models', 'deactivate_models']
    
    def request_count(self, obj):
        """Get number of requests for this model"""
        return obj.requests.count()
    request_count.short_description = 'Requests'
    
    def last_tested_display(self, obj):
        """Display last tested time"""
        if obj.last_tested:
            time_diff = timezone.now() - obj.last_tested
            if time_diff.days > 7:
                color = 'red'
            elif time_diff.days > 3:
                color = 'orange'
            else:
                color = 'green'
            return format_html(
                '<span style="color: {};">{}</span>',
                color,
                obj.last_tested.strftime('%Y-%m-%d %H:%M')
            )
        return format_html('<span style="color: red;">Never tested</span>')
    last_tested_display.short_description = 'Last Tested'
    
    def test_models(self, request, queryset):
        """Test selected AI models"""
        for model in queryset:
            # Here you would implement actual model testing
            model.last_tested = timezone.now()
            model.save()
        self.message_user(request, f"Tested {queryset.count()} models")
    test_models.short_description = "Test selected models"
    
    def activate_models(self, request, queryset):
        """Activate selected models"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Activated {updated} models")
    activate_models.short_description = "Activate selected models"
    
    def deactivate_models(self, request, queryset):
        """Deactivate selected models"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} models")
    deactivate_models.short_description = "Deactivate selected models"


@admin.register(AIRequest)
class AIRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for AI requests
    """
    list_display = [
        'id', 'user', 'ai_model', 'request_type', 'status', 
        'processing_time_display', 'tokens_used', 'cost_display', 'created_at'
    ]
    list_filter = [
        'status', 'request_type', 'ai_model__provider', 
        'ai_model__model_type', 'created_at'
    ]
    search_fields = ['user__username', 'input_text', 'output_text']
    readonly_fields = [
        'created_at', 'completed_at', 'processing_time', 
        'tokens_used', 'cost', 'ip_address', 'user_agent'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Info', {
            'fields': ('user', 'ai_model', 'request_type', 'status')
        }),
        ('Content', {
            'fields': ('input_text', 'output_text', 'prompt_template')
        }),
        ('Performance', {
            'fields': ('processing_time', 'tokens_used', 'cost', 'parameters')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Error Info', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        })
    )
    
    def processing_time_display(self, obj):
        """Display processing time in readable format"""
        if obj.processing_time:
            if obj.processing_time < 1:
                return f"{obj.processing_time * 1000:.0f}ms"
            else:
                return f"{obj.processing_time:.1f}s"
        return "-"
    processing_time_display.short_description = 'Processing Time'
    
    def cost_display(self, obj):
        """Display cost in readable format"""
        if obj.cost > 0:
            return f"${obj.cost:.4f}"
        return "$0.00"
    cost_display.short_description = 'Cost'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user', 'ai_model')


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    """
    Admin interface for prompt templates
    """
    list_display = [
        'name', 'template_type', 'is_active', 'usage_count', 
        'avg_rating_display', 'created_at'
    ]
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'template_text']
    filter_horizontal = ['recommended_models']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'template_type', 'is_active')
        }),
        ('Template Content', {
            'fields': ('template_text',)
        }),
        ('Variables', {
            'fields': ('required_variables', 'optional_variables')
        }),
        ('Configuration', {
            'fields': (
                'recommended_models', 'default_temperature', 
                'default_max_tokens'
            )
        }),
        ('Statistics', {
            'fields': ('usage_count', 'avg_rating'),
            'classes': ('collapse',)
        })
    )
    
    def avg_rating_display(self, obj):
        """Display average rating with stars"""
        if obj.avg_rating > 0:
            stars = "★" * int(obj.avg_rating) + "☆" * (5 - int(obj.avg_rating))
            return format_html(
                '<span title="{:.1f}/5">{}</span>',
                obj.avg_rating, stars
            )
        return "No ratings"
    avg_rating_display.short_description = 'Avg Rating'


@admin.register(UserAIUsage)
class UserAIUsageAdmin(admin.ModelAdmin):
    """
    Admin interface for user AI usage
    """
    list_display = [
        'user', 'requests_this_month', 'monthly_request_limit',
        'usage_percentage', 'tokens_this_month', 'cost_this_month',
        'is_quota_exceeded', 'last_request_date'
    ]
    list_filter = ['is_quota_exceeded', 'current_month']
    search_fields = ['user__username', 'user__email']
    readonly_fields = [
        'current_month', 'requests_this_month', 'tokens_this_month',
        'cost_this_month', 'total_requests', 'total_tokens', 'total_cost',
        'last_request_date', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Monthly Usage', {
            'fields': (
                'current_month', 'requests_this_month', 'tokens_this_month',
                'cost_this_month', 'is_quota_exceeded'
            )
        }),
        ('Limits', {
            'fields': (
                'monthly_request_limit', 'monthly_token_limit', 'monthly_cost_limit'
            )
        }),
        ('Lifetime Statistics', {
            'fields': ('total_requests', 'total_tokens', 'total_cost'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('last_request_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def usage_percentage(self, obj):
        """Calculate usage percentage"""
        if obj.monthly_request_limit > 0:
            percentage = (obj.requests_this_month / obj.monthly_request_limit) * 100
            if percentage >= 90:
                color = 'red'
            elif percentage >= 70:
                color = 'orange'
            else:
                color = 'green'
            return format_html(
                '<span style="color: {};">{:.1f}%</span>',
                color, percentage
            )
        return "0%"
    usage_percentage.short_description = 'Usage %'


@admin.register(AIFeedback)
class AIFeedbackAdmin(admin.ModelAdmin):
    """
    Admin interface for AI feedback
    """
    list_display = [
        'ai_request', 'quality_rating', 'usefulness_rating',
        'content_used', 'created_at'
    ]
    list_filter = [
        'quality_rating', 'usefulness_rating', 'content_used', 'created_at'
    ]
    search_fields = ['positive_aspects', 'negative_aspects', 'suggestions']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('ai_request',)
        }),
        ('Ratings', {
            'fields': ('quality_rating', 'usefulness_rating')
        }),
        ('Feedback', {
            'fields': ('positive_aspects', 'negative_aspects', 'suggestions')
        }),
        ('Usage', {
            'fields': ('content_used', 'modifications_made')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )


@admin.register(ContentAnalysis)
class ContentAnalysisAdmin(admin.ModelAdmin):
    """
    Admin interface for content analysis
    """
    list_display = [
        'content_type', 'content_id', 'readability_score',
        'sentiment_score', 'tone_classification', 'word_count', 'analyzed_at'
    ]
    list_filter = [
        'content_type', 'tone_classification', 'analyzed_at', 'ai_model_used'
    ]
    search_fields = ['content_text']
    readonly_fields = ['analyzed_at']
    
    fieldsets = (
        ('Content Info', {
            'fields': ('content_type', 'content_id', 'content_text')
        }),
        ('Analysis Results', {
            'fields': (
                'readability_score', 'sentiment_score', 'tone_classification',
                'word_count', 'reading_time', 'complexity_score'
            )
        }),
        ('SEO Analysis', {
            'fields': (
                'keyword_density', 'suggested_keywords', 
                'meta_description_suggestion', 'title_suggestions'
            )
        }),
        ('Suggestions', {
            'fields': ('improvement_suggestions', 'tag_suggestions')
        }),
        ('Metadata', {
            'fields': ('ai_model_used', 'analyzed_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AIGeneratedImage)
class AIGeneratedImageAdmin(admin.ModelAdmin):
    """
    Admin interface for AI generated images
    """
    list_display = [
        'image_preview', 'prompt_preview', 'ai_model', 'user',
        'used_in_content', 'generation_time', 'created_at'
    ]
    list_filter = [
        'ai_model', 'used_in_content', 'content_type', 'created_at'
    ]
    search_fields = ['prompt', 'negative_prompt']
    readonly_fields = ['generation_time', 'cost', 'created_at']
    
    fieldsets = (
        ('Generation Parameters', {
            'fields': ('prompt', 'negative_prompt', 'ai_model')
        }),
        ('Image Settings', {
            'fields': ('width', 'height', 'steps', 'guidance_scale', 'seed')
        }),
        ('Generated Images', {
            'fields': ('image_file', 'thumbnail')
        }),
        ('Usage Tracking', {
            'fields': ('used_in_content', 'content_type', 'content_id')
        }),
        ('Generation Stats', {
            'fields': ('generation_time', 'cost', 'user', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.thumbnail:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.thumbnail.url
            )
        elif obj.image_file:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image_file.url
            )
        return "No image"
    image_preview.short_description = 'Preview'
    
    def prompt_preview(self, obj):
        """Display truncated prompt"""
        return obj.prompt[:50] + "..." if len(obj.prompt) > 50 else obj.prompt
    prompt_preview.short_description = 'Prompt'


# Custom admin site configuration
class AIIntegrationAdminConfig:
    """
    Custom admin configuration for AI Integration
    """
    def __init__(self, admin_site):
        self.admin_site = admin_site
    
    def get_app_list(self, request):
        """
        Customize app list for AI Integration
        """
        app_list = self.admin_site.get_app_list(request)
        
        # Find AI Integration app and reorder models
        for app in app_list:
            if app['app_label'] == 'ai_integration':
                # Reorder models by importance
                model_order = [
                    'AIModel', 'AIRequest', 'PromptTemplate', 
                    'UserAIUsage', 'ContentAnalysis', 'AIFeedback',
                    'AIGeneratedImage'
                ]
                
                models_dict = {model['object_name']: model for model in app['models']}
                app['models'] = [models_dict[name] for name in model_order if name in models_dict]
                break
        
        return app_list


# Admin dashboard customizations
def ai_integration_dashboard_stats():
    """
    Get AI integration statistics for dashboard
    """
    from django.db.models import Sum, Avg, Count
    from datetime import datetime, timedelta
    
    # Calculate statistics
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_requests': AIRequest.objects.count(),
        'requests_today': AIRequest.objects.filter(created_at__date=today).count(),
        'requests_this_week': AIRequest.objects.filter(created_at__date__gte=week_ago).count(),
        'requests_this_month': AIRequest.objects.filter(created_at__date__gte=month_ago).count(),
        'success_rate': 0,
        'avg_processing_time': 0,
        'total_cost': 0,
        'active_models': AIModel.objects.filter(is_active=True).count(),
        'total_users': UserAIUsage.objects.count(),
        'quota_exceeded_users': UserAIUsage.objects.filter(is_quota_exceeded=True).count()
    }
    
    # Calculate success rate
    completed_requests = AIRequest.objects.filter(status='completed').count()
    if stats['total_requests'] > 0:
        stats['success_rate'] = (completed_requests / stats['total_requests']) * 100
    
    # Calculate average processing time
    avg_time = AIRequest.objects.filter(
        status='completed'
    ).aggregate(avg_time=Avg('processing_time'))['avg_time']
    if avg_time:
        stats['avg_processing_time'] = avg_time
    
    # Calculate total cost
    total_cost = AIRequest.objects.aggregate(total=Sum('cost'))['total']
    if total_cost:
        stats['total_cost'] = total_cost
    
    return stats


# Context processor for admin dashboard
def ai_admin_context(request):
    """
    Context processor to add AI stats to admin dashboard
    """
    if request.path.startswith('/admin/') and request.user.is_staff:
        return {
            'ai_stats': ai_integration_dashboard_stats()
        }
    return {}


# Admin action for bulk operations
def export_ai_requests_csv(modeladmin, request, queryset):
    """
    Export AI requests to CSV
    """
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ai_requests.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'User', 'Model', 'Request Type', 'Status',
        'Processing Time', 'Tokens Used', 'Cost', 'Created At'
    ])
    
    for request_obj in queryset:
        writer.writerow([
            request_obj.id,
            request_obj.user.username,
            request_obj.ai_model.name,
            request_obj.request_type,
            request_obj.status,
            request_obj.processing_time,
            request_obj.tokens_used,
            request_obj.cost,
            request_obj.created_at
        ])
    
    return response
export_ai_requests_csv.short_description = "Export selected requests to CSV"

# Add the action to AIRequestAdmin
AIRequestAdmin.actions.append(export_ai_requests_csv)


# Admin site customizations
admin.site.site_header = "Portfolio Platform Admin"
admin.site.site_title = "Portfolio Platform"
admin.site.index_title = "Welcome to Portfolio Platform Administration"


# Register additional admin views if needed
class AIAnalyticsView:
    """
    Custom admin view for AI analytics
    """
    def __init__(self):
        self.template_name = 'admin/ai_integration/analytics.html'
    
    def get_context_data(self):
        """
        Get analytics data for the view
        """
        stats = ai_integration_dashboard_stats()
        
        # Get top models by usage
        top_models = AIModel.objects.annotate(
            request_count=Count('requests')
        ).order_by('-request_count')[:5]
        
        # Get recent activity
        recent_requests = AIRequest.objects.select_related(
            'user', 'ai_model'
        ).order_by('-created_at')[:10]
        
        return {
            'stats': stats,
            'top_models': top_models,
            'recent_requests': recent_requests
        }


# Custom admin filters
class RequestStatusFilter(admin.SimpleListFilter):
    """
    Custom filter for AI request status
    """
    title = 'Request Status'
    parameter_name = 'status'
    
    def lookups(self, request, model_admin):
        return [
            ('completed', 'Completed'),
            ('failed', 'Failed'),
            ('processing', 'Processing'),
            ('pending', 'Pending')
        ]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class ModelProviderFilter(admin.SimpleListFilter):
    """
    Custom filter for AI model providers
    """
    title = 'Provider'
    parameter_name = 'provider'
    
    def lookups(self, request, model_admin):
        providers = AIModel.objects.values_list(
            'provider', flat=True
        ).distinct()
        return [(provider, provider.title()) for provider in providers]
    
    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ai_model__provider=self.value())
        return queryset


# Add custom filters to admin classes
AIRequestAdmin.list_filter = list(AIRequestAdmin.list_filter) + [
    RequestStatusFilter, ModelProviderFilter
]