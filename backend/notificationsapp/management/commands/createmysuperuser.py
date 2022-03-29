import os

from django.core.management import BaseCommand

from usersapp.models import User

NAME = os.environ.get('SUPERUSER')
PASS = os.environ.get('SUPERUSER_PASS')


class Command(BaseCommand):

    def handle(self, *args, **options):
        exists = User.objects.filter(username=NAME).first()
        if exists:
            self.stderr.write(self.style.ERROR(
                'Superuser with username "%s" already exists!' % NAME))
        else:
            new_user = User.objects.create_superuser(username=NAME,
                                                     email='',
                                                     password=PASS)
            new_user.is_verified = True
            new_user.save()
            self.stdout.write(self.style.SUCCESS('Superuser created!'))
