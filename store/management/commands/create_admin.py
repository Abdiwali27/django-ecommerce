import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create a Django superuser from environment variables"

    def handle(self, *args, **options):

        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Superuser environment variables are not set. Skipping."
                )
            )
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email or "",
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser '{username}' created successfully."
                )
            )

        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Superuser '{username}' already exists. Skipping."
                )
            )