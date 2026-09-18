"""Create the temporary administrator used for assessment."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


ADMIN_USERNAME = "examiner_admin"
ADMIN_EMAIL = "examiner@example.com"
ADMIN_PASSWORD = "ChangeMeNow!2026"


class Command(BaseCommand):
    """Create the default assessment administrator."""

    help = (
        "Creates the temporary administrator "
        "account used for assessment."
    )

    def handle(self, *args, **options):
        """Create the administrator if it does not exist."""

        user_model = get_user_model()

        if user_model.objects.filter(
            username=ADMIN_USERNAME
        ).exists():
            self.stdout.write(
                self.style.WARNING(
                    "The default administrator "
                    "already exists."
                )
            )

            self.stdout.write(
                "Username: "
                f"{ADMIN_USERNAME}"
            )

            return

        user_model.objects.create_superuser(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Default administrator created."
            )
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            f"Username: {ADMIN_USERNAME}"
        )

        self.stdout.write(
            f"Temporary password: "
            f"{ADMIN_PASSWORD}"
        )

        self.stdout.write(
            ""
        )

        self.stdout.write(
            self.style.WARNING(
                "IMPORTANT: Change this password "
                "after the first login."
            )
        )