from django.core.management.base import BaseCommand
from accounts.models import CustomUser

class Command(BaseCommand):
    help = 'Creates a new staff user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('email', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password']

        if not CustomUser.objects.filter(username=username).exists():
            CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True
            )
            self.stdout.write(self.style.SUCCESS(f'Staff user "{username}" created successfully'))
        else:
            self.stdout.write(self.style.ERROR(f'User with username "{username}" already exists'))