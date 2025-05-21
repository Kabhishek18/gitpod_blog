from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import BlogCategory, BlogAuthor
from wagtail.models import Site, Page

class Command(BaseCommand):
    help = 'Setup initial blog data including categories and sample content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-user',
            type=str,
            help='Username for the admin user (default: admin)',
            default='admin'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            help='Email for the admin user',
            default='admin@example.com'
        )

    def handle(self, *args, **options):
        self.stdout.write('Setting up blog data...')
        
        # Create or get admin user
        admin_username = options['admin_user']
        admin_email = options['admin_email']
        
        try:
            admin_user = User.objects.get(username=admin_username)
            self.stdout.write(f'Using existing admin user: {admin_username}')
        except User.DoesNotExist:
            admin_user = User.objects.create_user(
                username=admin_username,
                email=admin_email,
                password='admin123',  # Change this in production!
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: {admin_username}')
            )
            self.stdout.write(
                self.style.WARNING(f'Default password is "admin123" - please change it!')
            )
        
        # Create blog categories
        categories_data = [
            {
                'name': 'Technology',
                'slug': 'technology',
                'description': 'Articles about latest technology trends, programming, and software development',
                'color': '#007acc'
            },
            {
                'name': 'Web Development',
                'slug': 'web-development',
                'description': 'Frontend and backend web development tutorials and tips',
                'color': '#28a745'
            },
            {
                'name': 'AI & Machine Learning',
                'slug': 'ai-machine-learning',
                'description': 'Artificial Intelligence, Machine Learning, and Data Science topics',
                'color': '#6f42c1'
            },
            {
                'name': 'DevOps',
                'slug': 'devops',
                'description': 'DevOps practices, CI/CD, cloud computing, and infrastructure',
                'color': '#fd7e14'
            },
            {
                'name': 'Mobile Development',
                'slug': 'mobile-development',
                'description': 'iOS, Android, and cross-platform mobile app development',
                'color': '#20c997'
            },
            {
                'name': 'Tutorials',
                'slug': 'tutorials',
                'description': 'Step-by-step guides and how-to articles',
                'color': '#17a2b8'
            },
            {
                'name': 'Career',
                'slug': 'career',
                'description': 'Career advice, job tips, and professional development',
                'color': '#e83e8c'
            },
            {
                'name': 'Tools & Resources',
                'slug': 'tools-resources',
                'description': 'Useful tools, libraries, and resources for developers',
                'color': '#6c757d'
            }
        ]
        
        created_categories = 0
        for cat_data in categories_data:
            category, created = BlogCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            
            if created:
                created_categories += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'○ Category already exists: {category.name}')
                )
        
        # Create blog author profile for admin user
        try:
            blog_author = BlogAuthor.objects.get(user=admin_user)
            self.stdout.write(f'Blog author profile already exists for: {admin_user.username}')
        except BlogAuthor.DoesNotExist:
            blog_author = BlogAuthor.objects.create(
                user=admin_user,
                bio=f'<p>Welcome to my blog! I\'m {admin_user.get_full_name() or admin_user.username}, a passionate developer sharing insights about technology, programming, and more.</p>',
                website='https://example.com',
                github='https://github.com/username',
                linkedin='https://linkedin.com/in/username',
                twitter='https://twitter.com/username'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Created blog author profile for: {admin_user.username}')
            )
        
        # Update author stats
        blog_author.update_stats()
        
        self.stdout.write(f'\n{self.style.SUCCESS("="*50)}')
        self.stdout.write(f'{self.style.SUCCESS("Blog setup completed successfully!")}')
        self.stdout.write(f'Created {created_categories} new blog categories')
        self.stdout.write(f'Blog author profile ready for: {admin_user.username}')
        self.stdout.write(f'{self.style.SUCCESS("="*50)}')
        
        if created_categories > 0:
            self.stdout.write(f'\n{self.style.WARNING("Next steps:")}')
            self.stdout.write('1. Access the Wagtail admin at /admin/')
            self.stdout.write('2. Create your first blog post')
            self.stdout.write('3. Configure site settings')
            self.stdout.write('4. Customize your blog author profile')
            self.stdout.write('5. Add more categories if needed')
        
        self.stdout.write(f'\n{self.style.WARNING("Note:")}')
        self.stdout.write('Make sure to run migrations before using the blog:')
        self.stdout.write('python manage.py makemigrations')
        self.stdout.write('python manage.py migrate')