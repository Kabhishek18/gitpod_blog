#!/usr/bin/env python
"""
Portfolio Platform Setup Script
This script helps set up the complete portfolio platform with all necessary components.
"""

import os
import sys
import subprocess
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()


def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ Success: {description}")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {description}")
        print(f"Error: {e.stderr}")
        return False


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n🔍 Checking dependencies...")
    
    required_packages = [
        'django',
        'wagtail',
        'djangorestframework',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True


def create_directories():
    """Create necessary directories"""
    directories = [
        'static',
        'media',
        'templates',
        'staticfiles',
        'logs'
    ]
    
    print("\n📁 Creating directories...")
    for directory in directories:
        dir_path = project_dir / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ Created/verified: {directory}/")


def setup_database():
    """Setup database with migrations"""
    print("\n🗄️ Setting up database...")
    
    # Make migrations
    if not run_command("python manage.py makemigrations", "Creating migrations"):
        return False
    
    # Run migrations
    if not run_command("python manage.py migrate", "Running migrations"):
        return False
    
    return True


def setup_ai_models():
    """Setup AI models and prompt templates"""
    print("\n🤖 Setting up AI models and templates...")
    
    return run_command(
        "python manage.py setup_ai_models",
        "Setting up AI models and prompt templates"
    )


def setup_blog_data():
    """Setup blog categories and initial data"""
    print("\n📝 Setting up blog data...")
    
    return run_command(
        "python manage.py setup_blog_data",
        "Setting up blog categories and data"
    )


def create_superuser():
    """Create superuser if it doesn't exist"""
    print("\n👤 Setting up superuser...")
    
    from django.contrib.auth.models import User
    
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'
    
    if User.objects.filter(username=username).exists():
        print(f"✅ Superuser '{username}' already exists")
        return True
    
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Created superuser: {username}")
        print(f"📧 Email: {email}")
        print(f"🔒 Password: {password}")
        print("⚠️ Please change the password after first login!")
        return True
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        return False


def setup_wagtail_site():
    """Setup Wagtail site and pages"""
    print("\n🌐 Setting up Wagtail site...")
    
    from wagtail.models import Site, Page
    from blog.models import BlogIndexPage
    
    try:
        # Get or create root page
        root_page = Page.objects.filter(depth=1).first()
        if not root_page:
            print("❌ No root page found. Please run migrations first.")
            return False
        
        # Create blog index page if it doesn't exist
        blog_index = BlogIndexPage.objects.first()
        if not blog_index:
            blog_index = BlogIndexPage(
                title="Blog",
                slug="blog",
                intro="<p>Welcome to my blog! Here you'll find articles about technology, programming, and more.</p>"
            )
            root_page.add_child(instance=blog_index)
            blog_index.save()
            print("✅ Created blog index page")
        else:
            print("✅ Blog index page already exists")
        
        # Update site configuration
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.site_name = "Portfolio Platform"
            site.save()
            print("✅ Updated site configuration")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up Wagtail site: {e}")
        return False


def collect_static():
    """Collect static files"""
    print("\n📦 Collecting static files...")
    
    return run_command(
        "python manage.py collectstatic --noinput",
        "Collecting static files"
    )


def display_completion_info():
    """Display completion information and next steps"""
    print("\n" + "="*80)
    print("🎉 PORTFOLIO PLATFORM SETUP COMPLETED! 🎉")
    print("="*80)
    
    print("\n📋 SETUP SUMMARY:")
    print("├── ✅ Dependencies checked")
    print("├── ✅ Directories created")
    print("├── ✅ Database migrated")
    print("├── ✅ AI models configured")
    print("├── ✅ Blog data setup")
    print("├── ✅ Superuser created")
    print("├── ✅ Wagtail site configured")
    print("└── ✅ Static files collected")
    
    print("\n🔑 LOGIN CREDENTIALS:")
    print("├── Username: admin")
    print("├── Password: admin123")
    print("└── ⚠️  CHANGE PASSWORD AFTER FIRST LOGIN!")
    
    print("\n🌐 ACCESS POINTS:")
    print("├── Django Admin: http://localhost:8000/django-admin/")
    print("├── Wagtail Admin: http://localhost:8000/admin/")
    print("├── API Root: http://localhost:8000/api/")
    print("├── AI Integration: http://localhost:8000/ai/")
    print("└── Blog: http://localhost:8000/blog/")
    
    print("\n🚀 NEXT STEPS:")
    print("1. Start the development server:")
    print("   python manage.py runserver")
    print()
    print("2. Configure your environment variables:")
    print("   - HUGGING_FACE_API_TOKEN (for AI features)")
    print("   - EMAIL settings (for contact forms)")
    print("   - Database settings (for production)")
    print()
    print("3. Customize your platform:")
    print("   - Update site settings in Wagtail admin")
    print("   - Create your first blog post")
    print("   - Customize AI models and prompts")
    print("   - Add your content and portfolio items")
    print()
    print("4. Security considerations:")
    print("   - Change default admin password")
    print("   - Update SECRET_KEY for production")
    print("   - Configure proper database for production")
    print("   - Set up HTTPS for production")
    
    print("\n📚 DOCUMENTATION:")
    print("├── Django: https://docs.djangoproject.com/")
    print("├── Wagtail: https://docs.wagtail.org/")
    print("├── DRF: https://www.django-rest-framework.org/")
    print("└── API Docs: http://localhost:8000/api/docs/")
    
    print("\n" + "="*80)


def main():
    """Main setup function"""
    print("🏗️  PORTFOLIO PLATFORM SETUP")
    print("=" * 80)
    print("This script will set up your complete portfolio platform.")
    print("Make sure you have installed all requirements first!")
    print("=" * 80)
    
    # Check if user wants to continue
    response = input("\n🤔 Do you want to continue with the setup? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("Setup cancelled.")
        return
    
    setup_steps = [
        ("Checking dependencies", check_dependencies),
        ("Creating directories", create_directories),
        ("Setting up database", setup_database),
        ("Setting up AI models", setup_ai_models),
        ("Setting up blog data", setup_blog_data),
        ("Creating superuser", create_superuser),
        ("Setting up Wagtail site", setup_wagtail_site),
        ("Collecting static files", collect_static),
    ]
    
    failed_steps = []
    
    for step_name, step_function in setup_steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
                print(f"⚠️ Warning: {step_name} failed but continuing...")
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n⚠️ Some steps failed: {', '.join(failed_steps)}")
        print("You may need to run these manually or check the error messages above.")
    
    display_completion_info()
    
    if not failed_steps:
        print("\n🎊 All setup steps completed successfully!")
    else:
        print(f"\n⚠️ Setup completed with {len(failed_steps)} warnings.")
    
    print("\nYou can now start your server with: python manage.py runserver")


if __name__ == "__main__":
    main()