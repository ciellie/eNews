"""Serializers for the news REST API."""

from rest_framework import serializers

from .models import Article
from .models import CustomUser
from .models import Newsletter
from .models import Publisher


class UserSerializer(
    serializers.ModelSerializer
):
    """Serializer for application users."""

    class Meta:
        model = CustomUser

        fields = [
            "id",
            "username",
            "email",
            "role",
            "subscriptions_publishers",
            "subscriptions_journalists",
        ]

        read_only_fields = [
            "id",
            "role",
        ]


class PublisherSerializer(
    serializers.ModelSerializer
):
    """Serializer for publishers."""

    class Meta:
        model = Publisher

        fields = [
            "id",
            "name",
            "description",
            "editors",
            "journalists",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
        ]


class ArticleSerializer(
    serializers.ModelSerializer
):
    """Serializer for articles."""

    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    publisher_name = serializers.CharField(
        source="publisher.name",
        read_only=True,
    )

    class Meta:
        model = Article

        fields = [
            "id",
            "title",
            "content",
            "author",
            "author_name",
            "publisher",
            "publisher_name",
            "created_at",
            "approved",
        ]

        read_only_fields = [
            "id",
            "author",
            "created_at",
        ]

    def validate_approved(
        self,
        approved,
    ):
        """Only editors may approve articles."""

        request = self.context.get(
            "request"
        )

        if request is None:
            return approved

        current_approved = False

        if self.instance:
            current_approved = (
                self.instance.approved
            )

        # Only check when changing from
        # unapproved to approved.
        if (
            approved
            and not current_approved
        ):
            is_editor = (
                request.user.is_superuser
                or request.user.role
                == CustomUser.EDITOR
                or request.user.groups.filter(
                    name="Editor"
                ).exists()
            )

            if not is_editor:
                raise serializers.ValidationError(
                    "Only editors may approve "
                    "articles."
                )

        return approved

    def validate_publisher(
        self,
        publisher,
    ):
        """Check journalist membership of publisher."""

        request = self.context.get(
            "request"
        )

        if (
            publisher is None
            or request is None
        ):
            return publisher

        # Editors are allowed to update articles.
        if (
            request.user.is_superuser
            or request.user.role
            == CustomUser.EDITOR
            or request.user.groups.filter(
                name="Editor"
            ).exists()
        ):
            return publisher

        if not publisher.journalists.filter(
            pk=request.user.pk
        ).exists():
            raise serializers.ValidationError(
                "You are not a journalist "
                "for this publisher."
            )

        return publisher


class NewsletterSerializer(
    serializers.ModelSerializer
):
    """Serializer for newsletters."""

    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        model = Newsletter

        fields = [
            "id",
            "title",
            "description",
            "created_at",
            "author",
            "author_name",
            "articles",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "author",
        ]