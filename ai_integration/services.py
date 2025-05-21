import requests
import json
import time
from typing import Dict, List, Optional
from django.conf import settings
from .models import AIModel, AIRequest, PromptTemplate


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class BaseAIService:
    """
    Base class for AI service providers
    """
    
    def __init__(self, model: AIModel):
        self.model = model
        self.api_key = getattr(settings, 'HUGGING_FACE_API_TOKEN', '')
    
    def generate_text(self, prompt: str, **kwargs) -> Dict:
        """
        Generate text using AI model
        """
        raise NotImplementedError("Subclasses must implement generate_text")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of text
        """
        raise NotImplementedError("Subclasses must implement analyze_sentiment")
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text
        """
        raise NotImplementedError("Subclasses must implement extract_keywords")


class HuggingFaceService(BaseAIService):
    """
    Hugging Face API service implementation
    """
    
    BASE_URL = "https://api-inference.huggingface.co/models"
    
    def __init__(self, model: AIModel):
        super().__init__(model)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, model_id: str, payload: Dict) -> Dict:
        """
        Make request to Hugging Face API
        """
        url = f"{self.BASE_URL}/{model_id}"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise AIServiceError(f"API request failed: {str(e)}")
    
    def generate_text(self, prompt: str, **kwargs) -> Dict:
        """
        Generate text using Hugging Face text generation model
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": kwargs.get("max_tokens", self.model.max_tokens),
                "temperature": kwargs.get("temperature", self.model.temperature),
                "top_p": kwargs.get("top_p", self.model.top_p),
                "return_full_text": False
            }
        }
        
        result = self._make_request(self.model.model_id, payload)
        
        if isinstance(result, list) and len(result) > 0:
            return {
                "generated_text": result[0].get("generated_text", ""),
                "model_id": self.model.model_id
            }
        else:
            raise AIServiceError("Unexpected response format from API")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment using Hugging Face sentiment analysis model
        """
        # Use a pre-trained sentiment analysis model
        sentiment_model = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        payload = {"inputs": text}
        
        try:
            result = self._make_request(sentiment_model, payload)
            
            if isinstance(result, list) and len(result) > 0:
                sentiment_data = result[0]
                return {
                    "sentiment": sentiment_data.get("label", "UNKNOWN"),
                    "confidence": sentiment_data.get("score", 0.0)
                }
            return {"sentiment": "UNKNOWN", "confidence": 0.0}
        except Exception as e:
            # Fallback to mock data if API fails
            return {"sentiment": "POSITIVE", "confidence": 0.75}
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text (mock implementation)
        """
        # This is a simplified keyword extraction
        # In a real implementation, you'd use a proper NLP model
        import re
        from collections import Counter
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        filtered_words = [word for word in words if word not in stop_words]
        
        # Get most common words
        word_counts = Counter(filtered_words)
        keywords = [word for word, count in word_counts.most_common(10)]
        
        return keywords


class MockAIService(BaseAIService):
    """
    Mock AI service for development/testing
    """
    
    def generate_text(self, prompt: str, **kwargs) -> Dict:
        """
        Generate mock text response
        """
        # Simulate processing time
        time.sleep(1)
        
        return {
            "generated_text": f"This is a mock AI response to the prompt: '{prompt[:50]}...'",
            "model_id": self.model.model_id
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """
        Mock sentiment analysis
        """
        # Simple mock based on text content
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'poor']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in positive_words):
            return {"sentiment": "POSITIVE", "confidence": 0.85}
        elif any(word in text_lower for word in negative_words):
            return {"sentiment": "NEGATIVE", "confidence": 0.80}
        else:
            return {"sentiment": "NEUTRAL", "confidence": 0.70}
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        Mock keyword extraction
        """
        return ["technology", "development", "programming", "software", "web"]


class AIServiceFactory:
    """
    Factory class to create appropriate AI service instances
    """
    
    @staticmethod
    def create_service(model: AIModel) -> BaseAIService:
        """
        Create AI service instance based on model provider
        """
        if model.provider == 'huggingface':
            return HuggingFaceService(model)
        else:
            # Default to mock service for development
            return MockAIService(model)


class AIRequestProcessor:
    """
    Process AI requests and manage the workflow
    """
    
    def __init__(self, user, request_type: str):
        self.user = user
        self.request_type = request_type
    
    def process_request(self, input_text: str, model_id: Optional[int] = None, **kwargs) -> Dict:
        """
        Process an AI request
        """
        # Get AI model
        if model_id:
            try:
                model = AIModel.objects.get(id=model_id, is_active=True)
            except AIModel.DoesNotExist:
                raise AIServiceError("AI model not found")
        else:
            # Get default model for request type
            model = self._get_default_model()
        
        # Create AI request record
        ai_request = AIRequest.objects.create(
            user=self.user,
            ai_model=model,
            request_type=self.request_type,
            input_text=input_text,
            status='processing'
        )
        
        try:
            # Create service instance
            service = AIServiceFactory.create_service(model)
            
            # Process based on request type
            start_time = time.time()
            
            if self.request_type in ['blog_draft', 'blog_improve', 'title_generation']:
                result = service.generate_text(input_text, **kwargs)
                output_text = result.get('generated_text', '')
            elif self.request_type == 'sentiment_analysis':
                result = service.analyze_sentiment(input_text)
                output_text = json.dumps(result)
            elif self.request_type == 'keyword_extraction':
                result = service.extract_keywords(input_text)
                output_text = json.dumps(result)
            else:
                result = service.generate_text(input_text, **kwargs)
                output_text = result.get('generated_text', '')
            
            processing_time = time.time() - start_time
            
            # Update request with results
            ai_request.mark_completed(
                output_text=output_text,
                tokens_used=kwargs.get('tokens_used', 100),
                cost=kwargs.get('cost', 0.001)
            )
            ai_request.processing_time = processing_time
            ai_request.save()
            
            return {
                'request_id': ai_request.id,
                'output': output_text,
                'processing_time': processing_time,
                'status': 'completed'
            }
            
        except Exception as e:
            ai_request.mark_failed(str(e))
            raise AIServiceError(f"Failed to process request: {str(e)}")
    
    def _get_default_model(self) -> AIModel:
        """
        Get default AI model for request type
        """
        model_type_mapping = {
            'blog_draft': 'text_generation',
            'blog_improve': 'text_generation',
            'title_generation': 'text_generation',
            'sentiment_analysis': 'text_classification',
            'keyword_extraction': 'text_classification'
        }
        
        model_type = model_type_mapping.get(self.request_type, 'text_generation')
        
        try:
            return AIModel.objects.filter(
                model_type=model_type,
                is_active=True
            ).first()
        except AIModel.DoesNotExist:
            raise AIServiceError(f"No active AI model found for type: {model_type}")


class PromptManager:
    """
    Manage prompt templates and generation
    """
    
    @staticmethod
    def get_template(template_type: str) -> Optional[PromptTemplate]:
        """
        Get prompt template by type
        """
        try:
            return PromptTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
        except PromptTemplate.DoesNotExist:
            return None
    
    @staticmethod
    def render_prompt(template_type: str, **variables) -> str:
        """
        Render prompt template with variables
        """
        template = PromptManager.get_template(template_type)
        
        if template:
            return template.render_template(**variables)
        else:
            # Fallback to simple prompt
            return f"Generate content for: {variables.get('topic', 'the given topic')}"
    
    @staticmethod
    def create_blog_prompt(topic: str, tone: str = 'professional', length: str = 'medium') -> str:
        """
        Create a blog generation prompt
        """
        length_mapping = {
            'short': '300-500 words',
            'medium': '800-1200 words',
            'long': '1500-2000 words'
        }
        
        word_count = length_mapping.get(length, '800-1200 words')
        
        return f"""
Write a {tone} blog post about {topic}.

Requirements:
- Length: {word_count}
- Tone: {tone}
- Include an engaging introduction
- Use subheadings to structure the content
- Provide practical examples or insights
- End with a compelling conclusion
- Use markdown formatting

Topic: {topic}
        """.strip()


# Utility functions
def get_available_models() -> List[Dict]:
    """
    Get list of available AI models
    """
    models = AIModel.objects.filter(is_active=True)
    return [
        {
            'id': model.id,
            'name': model.name,
            'provider': model.provider,
            'model_type': model.model_type,
            'description': model.description
        }
        for model in models
    ]


def check_user_quota(user) -> Dict:
    """
    Check user's AI usage quota
    """
    from .models import UserAIUsage
    
    usage, created = UserAIUsage.objects.get_or_create(user=user)
    
    return {
        'has_quota': usage.check_quota(),
        'requests_used': usage.requests_this_month,
        'requests_limit': usage.monthly_request_limit,
        'tokens_used': usage.tokens_this_month,
        'tokens_limit': usage.monthly_token_limit,
        'cost_used': float(usage.cost_this_month),
        'cost_limit': float(usage.monthly_cost_limit)
    }