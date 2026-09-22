"""Serializers for the news REST API.

This module contains Django REST Framework serializers used to
convert application model instances to and from JSON-compatible
representations.

The serializers support the following models:

* :class:`news.models.CustomUser`
* :class:`news.models.Publisher`
* :class:`news.models.Article`
* :class:`news.models.Newsletter`

Validation is also performed for article approval and Publisher
membership.
"""

from rest_framework import serializers

from .models import Article
from .models import CustomUser
from .models import Newsletter
from .models import Publisher


class UserSerializer(
    serializers.ModelSerializer
):
    """Serialize application users.

    This serializer exposes basic user information, the application
    role, and Reader subscriptions.

    The user's ID and role are read-only through this serializer.

    :ivar Meta:
        Serializer metadata defining the model, exposed fields,
        and read-only fields.
    """

    class Meta:
        """Configure the user serializer."""

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
    """Serialize Publisher records.

    This serializer exposes Publisher information as well as the
    Editors and Journalists associated with the Publisher.

    The Publisher ID and creation date are read-only.

    :ivar Meta:
        Serializer metadata defining the Publisher model and fields.
    """

    class Meta:
        """Configure the Publisher serializer."""

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
    """Serialize news articles.

    The serializer provides the normal Article model fields together
    with convenient read-only representations of the author name and
    Publisher name.

    It also performs validation for:

    * article approval
    * Publisher membership

    :ivar author_name:
        Read-only username of the article author.
    :vartype author_name:
        rest_framework.serializers.CharField

    :ivar publisher_name:
        Read-only name of the Publisher associated with the article.
    :vartype publisher_name:
        rest_framework.serializers.CharField
    """

    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    publisher_name = serializers.CharField(
        source="publisher.name",
        read_only=True,
    )

    class Meta:
        """Configure the Article serializer."""

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
        """Validate changes to the article approval status.

        The method checks whether the current authenticated user has
        Editor privileges when an article changes from unapproved to
        approved.

        Superusers are also permitted to approve articles.

        If the approval value is not changing from ``False`` to
        ``True``, the value is returned without an Editor check.

        :param bool approved:
            The proposed approval value for the article.

        :returns:
            The validated approval value.

        :rtype:
            bool

        :raises serializers.ValidationError:
            If a non-Editor attempts to approve an article.
        """

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
        """Validate the selected Publisher.

        Journalists may only assign an article to a Publisher for
        which they are registered as a Journalist.

        Editors and superusers are permitted to work with Publisher
        articles without this Journalist membership check.

        A ``None`` Publisher value is valid because an article may
        instead be an independent Journalist article.

        :param Publisher publisher:
            The Publisher selected for the article.

        :returns:
            The validated Publisher instance, or ``None`` for an
            independent Journalist article.

        :rtype:
            Publisher or None

        :raises serializers.ValidationError:
            If a Journalist attempts to use a Publisher that they
            do not belong to.
        """

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
    """Serialize newsletters.

    The serializer exposes Newsletter details together with a
    read-only representation of the author's username.

    Articles associated with the Newsletter are represented through
    the Newsletter model's many-to-many relationship.

    :ivar author_name:
        Read-only username of the Newsletter author.
    :vartype author_name:
        rest_framework.serializers.CharField
    """

    author_name = serializers.CharField(
        source="author.username",
        read_only=True,
    )

    class Meta:
        """Configure the Newsletter serializer."""

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