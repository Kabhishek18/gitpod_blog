# Blog Platform with AI Integration

A comprehensive portfolio and blog platform built with Django, Wagtail CMS, and AI integration capabilities. Features include blog management, AI-assisted content creation, RESTful APIs, and a modern admin interface.

## ✨ Features

### 🎯 Core Features
- **Blog Management**: Full-featured blog with categories, tags, and rich content editing
- **Wagtail CMS**: Powerful content management with StreamFields and flexible page structures
- **RESTful API**: Complete API for blog posts, categories, search, and analytics
- **Responsive Design**: Mobile-friendly interface with modern styling

### 🤖 AI Integration
- **Content Generation**: AI-powered blog draft creation and content improvement
- **SEO Optimization**: Automatic meta descriptions and keyword suggestions
- **Text Analysis**: Sentiment analysis, readability scoring, and tone detection
- **Smart Suggestions**: Title generation, tag suggestions, and content recommendations
- **Multiple AI Providers**: Support for Hugging Face, OpenAI, and other AI services

### 📊 Analytics & Insights
- **Usage Analytics**: Track AI usage, costs, and performance metrics
- **Content Analytics**: Blog performance, view counts, and engagement metrics
- **User Management**: Quota management and usage tracking per user

### 🛠️ Developer Tools
- **Management Commands**: Easy setup and data migration tools
- **Comprehensive Admin**: Django and Wagtail admin interfaces
- **API Documentation**: Auto-generated API documentation
- **Extensible Architecture**: Modular design for easy customization

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Django 5.1+
- Node.js (for frontend dependencies, if needed)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd portfolio-platform
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run automated setup**
```bash
python setup_project.py
```

The setup script will:
- Create necessary directories
- Run database migrations
- Set up AI models and prompt templates
- Create blog categories
- Create a superuser account
- Configure Wagtail site settings

### Manual Setup (Alternative)

If you prefer manual setup:

```bash
# Create directories
mkdir -p static media templates staticfiles logs

# Database setup
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Setup AI models and blog data
python manage.py setup_ai_models
python manage.py setup_blog_data

# Collect static files
python manage.py collectstatic
```

### 🏃‍♂️ Run the Application

```bash
python manage.py runserver
```

Access the application:
- **Main site**: http://localhost:8000/
- **Wagtail Admin**: http://localhost:8000/admin/
- **Django Admin**: http://localhost:8000/django-admin/
- **API Root**: http://localhost:8000/api/
- **API Documentation**: http://localhost:8000/api/docs/

### Default Credentials
- **Username**: admin
- **Password**: admin123

⚠️ **Important**: Change the default password after first login!

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (for production)
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# AI Integration
HUGGING_FACE_API_TOKEN=your-huggingface-token
OPENAI_API_KEY=your-openai-key

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cache (Redis)
REDIS_URL=redis://localhost:6379/0
```

### AI Models Configuration

The platform supports multiple AI providers:

1. **Hugging Face** (Default)
   - Free tier available
   - Multiple models for different tasks
   - Get your token: https://huggingface.co/settings/tokens

2. **OpenAI** (Optional)
   - Requires API key and billing
   - Higher quality responses
   - Get your key: https://platform.openai.com/api-keys

3. **Custom Models**
   - Add your own AI service integrations
   - Extend the `BaseAIService` class

## 📖 Usage Guide

### Blog Management

1. **Access Wagtail Admin**: http://localhost:8000/admin/
2. **Create Blog Posts**: 
   - Navigate to Pages > Blog
   - Add new blog post
   - Use StreamField for rich content
3. **Manage Categories**: 
   - Go to Snippets > Blog Categories
   - Add/edit categories with colors

### AI Features

1. **Generate Blog Drafts**:
```bash
curl -X POST http://localhost:8000/ai/blog/generate-draft/ \
  -H "Content-Type: application/json" \
  -d '{"topic": "Django Best Practices", "tone": "professional", "length": "medium"}'
```

2. **Improve Content**:
```bash
curl -X POST http://localhost:8000/ai/blog/improve-content/ \
  -H "Content-Type: application/json" \
  -d '{"content": "Your blog content here", "type": "readability"}'
```

3. **SEO Optimization**:
```bash
curl -X POST http://localhost:8000/ai/blog/seo-optimize/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Your Title", "content": "Your content", "keyword": "target keyword"}'
```

### API Usage

#### Get Blog Posts
```bash
curl http://localhost:8000/api/blog/
```

#### Search Content
```bash
curl "http://localhost:8000/api/search/?q=django"
```

#### Blog Analytics
```bash
curl http://localhost:8000/api/blog/stats/
```

## 🏗️ Project Structure

```
portfolio-platform/
├── core/                    # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── blog/                   # Blog application
│   ├── models.py          # Blog models (Wagtail pages)
│   ├── admin.py           # Admin configuration
│   └── management/        # Management commands
├── api/                    # REST API application
│   ├── views.py           # API views and viewsets
│   ├── serializers.py     # API serializers
│   └── urls.py            # API routing
├── ai_integration/         # AI features application
│   ├── models.py          # AI models and requests
│   ├── views.py           # AI API endpoints
│   ├── services.py        # AI service providers
│   ├── admin.py           # AI admin interface
│   └── management/        # AI setup commands
├── templates/             # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploads
├── requirements.txt      # Python dependencies
├── setup_project.py     # Automated setup script
└── README.md            # This file
```

## 🔌 API Endpoints

### Blog API
- `GET /api/blog/` - List blog posts
- `GET /api/blog/{id}/` - Get blog post details
- `GET /api/blog/popular/` - Popular posts
- `GET /api/blog/recent/` - Recent posts

### AI API
- `POST /ai/blog/generate-draft/` - Generate blog draft
- `POST /ai/blog/improve-content/` - Improve existing content
- `POST /ai/blog/generate-title/` - Generate titles
- `POST /ai/blog/seo-optimize/` - SEO optimization
- `GET /ai/usage/` - AI usage statistics

### Utility API
- `GET /api/search/` - Global search
- `GET /api/health/` - Health check
- `GET /api/version/` - Version information
- `POST /api/contact/` - Contact form

## 🛠️ Development

### Adding New AI Features

1. **Create AI Service Method**:
```python
# In ai_integration/services.py
def your_new_feature(self, text: str) -> Dict:
    # Implement your AI logic
    pass
```

2. **Add API Endpoint**:
```python
# In ai_integration/views.py
class YourNewFeatureView(BaseAIView):
    def post(self, request):
        # Handle the request
        pass
```

3. **Register URL**:
```python
# In ai_integration/urls.py
path('your-feature/', views.YourNewFeatureView.as_view(), name='your-feature'),
```

### Extending Blog Models

```python
# In blog/models.py
class BlogPage(Page):
    # Add your custom fields
    custom_field = models.CharField(max_length=100)
    
    content_panels = Page.content_panels + [
        FieldPanel('custom_field'),
    ]
```

### Custom AI Providers

```python
# In ai_integration/services.py
class CustomAIService(BaseAIService):
    def generate_text(self, prompt: str, **kwargs) -> Dict:
        # Implement your custom AI provider
        pass
```

## 🧪 Testing

Run tests:
```bash
python manage.py test
```

Run specific app tests:
```bash
python manage.py test blog
python manage.py test ai_integration
python manage.py test api
```

## 🚀 Deployment

### Production Settings

1. **Update settings for production**:
```python
# In core/settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'your_db_host',
        'PORT': '5432',
    }
}
```

2. **Collect static files**:
```bash
python manage.py collectstatic
```

3. **Use production WSGI server**:
```bash
pip install gunicorn
gunicorn core.wsgi:application
```

### Docker Deployment

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "core.wsgi:application"]
```

## 📚 Documentation

- **API Documentation**: Available at `/api/docs/` when running
- **Wagtail Documentation**: https://docs.wagtail.org/
- **Django Documentation**: https://docs.djangoproject.com/
- **DRF Documentation**: https://www.django-rest-framework.org/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

If you encounter any issues or have questions:

1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information

## 🙏 Acknowledgments

- Django and Wagtail communities
- Hugging Face for AI model APIs
- All contributors and testers

---

Built with ❤️ using Django, Wagtail, and AI technologies.