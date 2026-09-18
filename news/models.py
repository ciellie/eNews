"""Database models for the news application."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class CustomUser(AbstractUser):
    """Custom application user."""

    READER = "READER"
    JOURNALIST = "JOURNALIST"
    EDITOR = "EDITOR"
    PUBLISHER = "PUBLISHER"

    ROLE_CHOICES = [
        (
            READER,
            "Reader",
        ),
        (
            JOURNALIST,
            "Journalist",
        ),
        (
            EDITOR,
            "Editor",
        ),
        (
            PUBLISHER,
            "Publisher",
        ),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=READER,
    )

    subscriptions_publishers = (
        models.ManyToManyField(
            "Publisher",
            blank=True,
            related_name="subscribers",
        )
    )

    subscriptions_journalists = (
        models.ManyToManyField(
            "self",
            blank=True,
            symmetrical=False,
            related_name=(
                "journalist_subscribers"
            ),
        )
    )

    def __str__(self):
        return self.username


class Publisher(models.Model):
    """A news Publisher."""

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_publisher",
        null=True,
        blank=True,
    )

    name = models.CharField(
        max_length=150,
    )

    description = models.TextField(
        blank=True,
    )

    editors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="editor_publishers",
    )

    journalists = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="journalist_publishers",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name

class Article(models.Model):
    """Represents an independent or publisher news article."""

    title = models.CharField(
        max_length=250,
    )

    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="independent_articles",
        limit_choices_to={
            "role": CustomUser.JOURNALIST,
        },
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    approved = models.BooleanField(
        default=False,
    )

    def clean(self):
        """Validate the article author and publisher."""

        super().clean()

        # Article cannot have both an independent
        # journalist and a publisher.
        if self.author and self.publisher:
            raise ValidationError(
                "An article cannot have both an "
                "independent author and publisher."
            )

        # Article must belong to either an
        # independent journalist or publisher.
        if (
            self.author is None
            and self.publisher is None
        ):
            raise ValidationError(
                "An article must have either a "
                "journalist or publisher."
            )

        # Only journalists can independently
        # publish articles.
        if (
            self.author
            and self.author.role
            != CustomUser.JOURNALIST
        ):
            raise ValidationError(
                "Independent articles must be "
                "written by a journalist."
            )

    def save(self, *args, **kwargs):
        """Validate before saving the article."""

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        """Return the article title."""
        return self.title


class Newsletter(models.Model):
    """Curated collection of news articles."""

    title = models.CharField(
        max_length=250,
    )

    description = models.TextField(
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="newsletters",
        limit_choices_to=Q(
            role__in=[
                CustomUser.JOURNALIST,
                CustomUser.EDITOR,
            ]
        ),
    )

    articles = models.ManyToManyField(
        Article,
        blank=True,
        related_name="newsletters",
    )

    def clean(self):

        """Validate the newsletter author."""

        super().clean()

        if self.author_id is None:
            return

        if self.author.role not in [
            CustomUser.JOURNALIST,
            CustomUser.EDITOR,
        ]:
            raise ValidationError(
                {
                    "author": (
                        "Newsletter author must be "
                        "a Journalist or Editor."
                    )
                }
            )

    def save(self, *args, **kwargs):
        """Validate before saving the newsletter."""

        self.full_clean()

        super().save(
            *args,
            **kwargs,
        )

    def __str__(self):
        """Return the newsletter title."""
        return self.title