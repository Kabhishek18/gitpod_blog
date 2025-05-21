from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Create admin superuser'

    def handle(self, *args, **options):
        username = 'admin'
        email = 'admin@example.com'
        password = 'admin123'
        
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if not user.is_superuser:
                user.is_superuser = True
                user.is_staff = True
                user.save()
                self.stdout.write(f'Made {username} a superuser')
            else:
                self.stdout.write(f'Superuser {username} already exists')
        else:
            User.objects.create_superuser(username, email, password)
            self.stdout.write(f'Created superuser: {username} / {password}')
            self.stdout.write('⚠️ Please change the default password!')
