from django.core.management.base import BaseCommand
from ai_integration.models import AIModel, PromptTemplate


class Command(BaseCommand):
    help = 'Setup initial AI models and prompt templates'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset existing models and templates',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing AI models and templates...')
            AIModel.objects.all().delete()
            PromptTemplate.objects.all().delete()
        
        self.stdout.write('Setting up AI models...')
        
        # Create AI models
        models_data = [
            {
                'name': 'Mistral 7B Instruct',
                'provider': 'huggingface',
                'model_id': 'mistralai/Mistral-7B-Instruct-v0.1',
                'model_type': 'text_generation',
                'description': 'A powerful 7B parameter language model optimized for instruction following and text generation tasks.',
                'max_tokens': 1024,
                'temperature': 0.7,
                'top_p': 0.9,
                'rate_limit': 60,
                'api_endpoint': 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1'
            },
            {
                'name': 'RoBERTa Sentiment Analysis',
                'provider': 'huggingface',
                'model_id': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
                'model_type': 'text_classification',
                'description': 'Fine-tuned RoBERTa model for sentiment analysis, trained on Twitter data.',
                'max_tokens': 512,
                'temperature': 0.1,
                'top_p': 0.9,
                'rate_limit': 100,
                'api_endpoint': 'https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest'
            },
            {
                'name': 'BART Large CNN Summarization',
                'provider': 'huggingface',
                'model_id': 'facebook/bart-large-cnn',
                'model_type': 'summarization',
                'description': 'BART model fine-tuned for summarization tasks, particularly effective for news articles.',
                'max_tokens': 1024,
                'temperature': 0.5,
                'top_p': 0.9,
                'rate_limit': 50,
                'api_endpoint': 'https://api-inference.huggingface.co/models/facebook/bart-large-cnn'
            },
            {
                'name': 'DistilBERT Question Answering',
                'provider': 'huggingface',
                'model_id': 'distilbert-base-cased-distilled-squad',
                'model_type': 'question_answering',
                'description': 'Lightweight BERT model fine-tuned for question answering tasks.',
                'max_tokens': 512,
                'temperature': 0.3,
                'top_p': 0.95,
                'rate_limit': 80,
                'api_endpoint': 'https://api-inference.huggingface.co/models/distilbert-base-cased-distilled-squad'
            },
            {
                'name': 'Stable Diffusion 2.1',
                'provider': 'huggingface',
                'model_id': 'stabilityai/stable-diffusion-2-1',
                'model_type': 'image_generation',
                'description': 'Latest Stable Diffusion model for generating high-quality images from text prompts.',
                'max_tokens': 77,
                'temperature': 0.0,
                'top_p': 1.0,
                'rate_limit': 30,
                'api_endpoint': 'https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1'
            }
        ]
        
        created_models = 0
        for model_data in models_data:
            model, created = AIModel.objects.get_or_create(
                provider=model_data['provider'],
                model_id=model_data['model_id'],
                defaults=model_data
            )
            
            if created:
                created_models += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created AI model: {model.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'○ AI model already exists: {model.name}')
                )
        
        # Create prompt templates
        self.stdout.write('\nSetting up prompt templates...')
        
        templates_data = [
            {
                'name': 'Blog Draft Generator',
                'template_type': 'blog_draft',
                'description': 'Generate comprehensive blog post drafts based on topic and requirements',
                'template_text': '''Write a {tone} blog post about {topic}.

Requirements:
- Length: approximately {length} words
- Tone: {tone}
- Target audience: {audience}
- Include an engaging introduction that hooks the reader
- Use clear subheadings to structure the content
- Provide practical examples, insights, or actionable advice
- Include relevant statistics or facts where appropriate
- End with a compelling conclusion that summarizes key points
- Use markdown formatting for better readability

{additional_instructions}

Topic: {topic}
Focus keywords: {keywords}''',
                'required_variables': ['topic', 'tone', 'length'],
                'optional_variables': ['audience', 'keywords', 'additional_instructions'],
                'default_temperature': 0.7,
                'default_max_tokens': 1024
            },
            {
                'name': 'SEO Meta Description Generator',
                'template_type': 'seo_meta',
                'description': 'Generate SEO-optimized meta descriptions for web pages',
                'template_text': '''Generate a compelling SEO meta description for the following content:

Title: {title}
Content: {content}
Primary keyword: {keyword}
Target audience: {audience}

Requirements:
- Maximum 155-160 characters
- Include the primary keyword naturally
- Make it engaging and click-worthy
- Include a subtle call to action
- Accurately represent the content
- Use active voice when possible

Meta description:''',
                'required_variables': ['title', 'content'],
                'optional_variables': ['keyword', 'audience'],
                'default_temperature': 0.5,
                'default_max_tokens': 256
            },
            {
                'name': 'Content Improver',
                'template_type': 'blog_improve',
                'description': 'Enhance existing content for better readability and engagement',
                'template_text': '''Improve the following content by focusing on {improvement_focus}:

Original content:
{content}

Improvement guidelines:
- Enhance clarity and readability
- Improve sentence structure and flow
- Add engaging elements where appropriate
- Optimize for SEO with target keyword: {keyword}
- Maintain the original tone and intent
- Fix any grammar or spelling issues
- Add transition words for better flow
- Break up long paragraphs if needed

Please provide the improved version:''',
                'required_variables': ['content'],
                'optional_variables': ['keyword', 'improvement_focus'],
                'default_temperature': 0.6,
                'default_max_tokens': 1024
            },
            {
                'name': 'Blog Title Generator',
                'template_type': 'title_generation',
                'description': 'Generate multiple engaging and SEO-friendly blog post titles',
                'template_text': '''Generate 8 engaging and SEO-friendly blog post titles for the following:

Topic: {topic}
Primary keywords: {keywords}
Target audience: {audience}
Tone: {tone}
Content type: {content_type}

Requirements for each title:
- Include relevant keywords naturally
- Make them clickable and engaging
- Optimize for search engines
- Keep under 60 characters when possible
- Use power words and emotional triggers
- Vary the title formats (how-to, lists, questions, etc.)
- Ensure accuracy and avoid clickbait

Generated titles:
1.
2.
3.
4.
5.
6.
7.
8.''',
                'required_variables': ['topic'],
                'optional_variables': ['keywords', 'audience', 'tone', 'content_type'],
                'default_temperature': 0.8,
                'default_max_tokens': 512
            },
            {
                'name': 'Grammar and Style Fixer',
                'template_type': 'grammar_fix',
                'description': 'Fix grammar errors and improve writing style',
                'template_text': '''Please fix any grammar errors and improve the writing quality of the following text:

Original text:
{text}

Focus on:
- Correcting grammar and spelling errors
- Improving sentence structure
- Enhancing clarity and readability
- Maintaining consistent tone
- Fixing punctuation issues
- Improving word choice where appropriate

Corrected version:''',
                'required_variables': ['text'],
                'optional_variables': ['style_guide', 'tone_preference'],
                'default_temperature': 0.2,
                'default_max_tokens': 1024
            },
            {
                'name': 'Content Summarizer',
                'template_type': 'content_summarize',
                'description': 'Create concise summaries of longer content',
                'template_text': '''Create a {summary_type} summary of the following content:

Content to summarize:
{content}

Summary requirements:
- Length: {length} ({word_limit})
- Focus on key points and main ideas
- Maintain the original meaning and context
- Use clear and concise language
- Include important statistics or facts
- Structure with bullet points if appropriate

Summary:''',
                'required_variables': ['content'],
                'optional_variables': ['summary_type', 'length', 'word_limit'],
                'default_temperature': 0.4,
                'default_max_tokens': 512
            },
            {
                'name': 'Tone Adjuster',
                'template_type': 'tone_adjustment',
                'description': 'Adjust the tone of content to match target style',
                'template_text': '''Rewrite the following content to match a {target_tone} tone:

Original content:
{content}

Target tone: {target_tone}
Target audience: {audience}

Guidelines for {target_tone} tone:
{tone_guidelines}

Maintain:
- The core message and information
- Key facts and data
- Overall structure and flow

Adjusted content:''',
                'required_variables': ['content', 'target_tone'],
                'optional_variables': ['audience', 'tone_guidelines'],
                'default_temperature': 0.6,
                'default_max_tokens': 1024
            }
        ]
        
        created_templates = 0
        for template_data in templates_data:
            template, created = PromptTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults=template_data
            )
            
            if created:
                created_templates += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created prompt template: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'○ Prompt template already exists: {template.name}')
                )
        
        # Summary
        self.stdout.write(f'\n{self.style.SUCCESS("="*50)}')
        self.stdout.write(f'{self.style.SUCCESS("Setup completed successfully!")}')
        self.stdout.write(f'Created {created_models} new AI models')
        self.stdout.write(f'Created {created_templates} new prompt templates')
        self.stdout.write(f'{self.style.SUCCESS("="*50)}')
        
        if created_models > 0 or created_templates > 0:
            self.stdout.write(f'\n{self.style.WARNING("Next steps:")}')
            self.stdout.write('1. Configure your HUGGING_FACE_API_TOKEN in settings')
            self.stdout.write('2. Test the AI models in the admin interface')
            self.stdout.write('3. Customize prompt templates as needed')
            self.stdout.write('4. Set up user quotas and limits')