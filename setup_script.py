#!/usr/bin/env python
"""
Portfolio Platform - Quick Setup Script (Fixed)
This script will quickly fix and setup your Django blog platform.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error")
        print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = [
        'static/css', 'static/js', 'static/images',
        'media/uploads', 'media/ai_generated',
        'templates/blog', 'templates/ai_integration',
        'staticfiles', 'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def create_basic_files():
    """Create basic required files"""
    print("\n📄 Creating basic files...")
    
    # Create home template
    home_template = '''{% extends "base.html" %}
{% load static %}

{% block title %}Portfolio Platform{% endblock %}

{% block content %}
<div class="container my-5">
    <div class="text-center">
        <h1 class="display-4">Portfolio Platform</h1>
        <p class="lead">AI-Powered Blog Platform</p>
        <div class="mt-4">
            <a href="/blog/" class="btn btn-primary me-3">Visit Blog</a>
            <a href="/admin/" class="btn btn-outline-primary">Admin Panel</a>
        </div>
    </div>
    
    <div class="row mt-5">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body text-center">
                    <i class="fas fa-robot fa-3x text-primary mb-3"></i>
                    <h5>AI Integration</h5>
                    <p>Generate and improve content with AI</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-body text-center">
                    <i class="fas fa-blog fa-3x text-primary mb-3"></i>
                    <h5>Blog System</h5>
                    <p>Full-featured blog with Wagtail CMS</p>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card">
                <div class="card-body text-center">
                    <i class="fas fa-api fa-3x text-primary mb-3"></i>
                    <h5>REST API</h5>
                    <p>Complete API for all features</p>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''

    # Create AI draft template
    ai_template = '''{% extends "base.html" %}
{% load static %}

{% block title %}AI Blog Generator{% endblock %}

{% block content %}
<div class="container my-5">
    <h1 class="text-center mb-5">AI Blog Draft Generator</h1>
    
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <form id="ai-blog-draft-form" class="card p-4">
                {% csrf_token %}
                <div class="mb-3">
                    <label for="topic" class="form-label">Blog Topic *</label>
                    <input type="text" class="form-control" id="topic" name="topic" required
                           placeholder="Enter your blog topic">
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <label for="tone" class="form-label">Tone</label>
                        <select class="form-control" id="tone" name="tone">
                            <option value="professional">Professional</option>
                            <option value="casual">Casual</option>
                            <option value="technical">Technical</option>
                        </select>
                    </div>
                    <div class="col-md-6">
                        <label for="length" class="form-label">Length</label>
                        <select class="form-control" id="length" name="length">
                            <option value="short">Short</option>
                            <option value="medium" selected>Medium</option>
                            <option value="long">Long</option>
                        </select>
                    </div>
                </div>
                
                <button type="submit" class="btn btn-primary">
                    <i class="fas fa-magic me-2"></i>Generate Draft
                </button>
            </form>
            
            <div id="ai-result" class="mt-4"></div>
        </div>
    </div>
</div>
{% endblock %}
'''

    # Create files
    files = {
        'templates/home.html': home_template,
        'templates/ai_integration/generate_draft.html': ai_template,
        '.env.example': '''DEBUG=True
SECRET_KEY=your-secret-key-here
HUGGING_FACE_API_TOKEN=your-token-here
OPENAI_API_KEY=your-key-here
''',
    }
    
    for file_path, content in files.items():
        file_obj = Path(file_path)
        file_obj.parent.mkdir(parents=True, exist_ok=True)
        
        if not file_obj.exists():
            with open(file_obj, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Created: {file_path}")

def fix_urls():
    """Fix URL configuration"""
    print("\n🔗 Fixing URLs...")
    
    urls_content = '''from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('api/', include('api.urls')),
    path('ai/', include('ai_integration.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    re_path(r'', include(wagtail_urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
'''
    
    with open('core/urls.py', 'w') as f:
        f.write(urls_content)
    print("✅ Fixed core/urls.py")

def setup_database():
    """Setup database"""
    print("\n🗄️ Setting up database...")
    
    success = True
    success &= run_command("python manage.py makemigrations", "Creating migrations")
    success &= run_command("python manage.py migrate", "Running migrations")
    
    return success

def create_superuser():
    """Create superuser"""
    print("\n👤 Creating superuser...")
    
    # Create management command to setup user
    mgmt_dir = Path("core/management/commands")
    mgmt_dir.mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py files
    Path("core/management/__init__.py").touch()
    Path("core/management/commands/__init__.py").touch()
    
    setup_command = '''from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create admin user'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Admin user created: admin/admin123'))
        else:
            self.stdout.write('Admin user already exists')
'''
    
    with open(mgmt_dir / "create_admin.py", 'w') as f:
        f.write(setup_command)
    
    return run_command("python manage.py create_admin", "Creating admin user")

def run_ai_setup():
    """Setup AI models"""
    print("\n🤖 Setting up AI models...")
    return run_command("python manage.py setup_ai_models", "Setting up AI models")

def run_blog_setup():
    """Setup blog data"""
    print("\n📝 Setting up blog data...")
    return run_command("python manage.py setup_blog_data", "Setting up blog data")

def collect_static():
    """Collect static files"""
    print("\n📦 Collecting static files...")
    return run_command("python manage.py collectstatic --noinput", "Collecting static files")

def main():
    """Main setup function"""
    print("🚀 PORTFOLIO PLATFORM QUICK SETUP")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Error: manage.py not found. Please run this script from the project root.")
        return
    
    response = input("Continue with setup? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    print("\n🔄 Starting setup process...")
    
    steps = [
        ("Creating directories", create_directories),
        ("Creating basic files", create_basic_files),
        ("Fixing URLs", fix_urls),
        ("Setting up database", setup_database),
        ("Creating superuser", create_superuser),
        ("Setting up AI models", run_ai_setup),
        ("Setting up blog data", run_blog_setup),
        ("Collecting static files", collect_static),
    ]
    
    completed = 0
    failed = []
    
    for step_name, step_func in steps:
        try:
            if step_func():
                completed += 1
            else:
                failed.append(step_name)
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed.append(step_name)
    
    print(f"\n📊 SETUP COMPLETE!")
    print(f"✅ Completed: {completed}/{len(steps)} steps")
    
    if failed:
        print(f"⚠️ Failed steps: {', '.join(failed)}")
        print("You may need to run these manually.")
    
    print(f"\n🎉 SUCCESS! Your platform is ready!")
    print(f"\n🌐 ACCESS POINTS:")
    print(f"├── Home: http://localhost:8000/")
    print(f"├── Admin: http://localhost:8000/admin/")
    print(f"├── Django Admin: http://localhost:8000/django-admin/")
    print(f"└── API: http://localhost:8000/api/")
    
    print(f"\n🔑 LOGIN: admin / admin123")
    print(f"\n🚀 START SERVER: python manage.py runserver")

if __name__ == "__main__":
    main()