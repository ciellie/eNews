"""Signals for users, permissions, and article approval."""

import logging

import requests

from django.conf import settings
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.core.mail import send_mail
from django.db import transaction
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Article
from .models import CustomUser


logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_groups_and_permissions(
    sender,
    **kwargs,
):
    """Create role groups and assign permissions."""

    if sender.name != "news":
        return

    reader_group, _ = Group.objects.get_or_create(
        name="Reader"
    )

    editor_group, _ = Group.objects.get_or_create(
        name="Editor"
    )

    journalist_group, _ = Group.objects.get_or_create(
        name="Journalist"
    )

    publisher_group, _ = Group.objects.get_or_create(
        name="Publisher"
    )

    # Reader:
    # Can only view articles and newsletters.
    reader_permissions = Permission.objects.filter(
        content_type__app_label="news",
        codename__in=[
            "view_article",
            "view_newsletter",
        ],
    )

    # Editor:
    # Can view, update, and delete.
    #
    # NOTE:
    # Being in this group does NOT automatically
    # give approval rights.
    # Publisher membership is checked separately
    # in the application.
    editor_permissions = Permission.objects.filter(
        content_type__app_label="news",
        codename__in=[
            "view_article",
            "change_article",
            "delete_article",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
        ],
    )

    # Journalist:
    # Can create, view, update, and delete.
    journalist_permissions = Permission.objects.filter(
        content_type__app_label="news",
        codename__in=[
            "add_article",
            "view_article",
            "change_article",
            "delete_article",
            "add_newsletter",
            "view_newsletter",
            "change_newsletter",
            "delete_newsletter",
        ],
    )

    # Publisher:
    # Publisher functionality such as managing
    # employees is controlled by the frontend
    # views and ownership checks.
    publisher_permissions = Permission.objects.none()

    reader_group.permissions.set(
        reader_permissions
    )

    editor_group.permissions.set(
        editor_permissions
    )

    journalist_group.permissions.set(
        journalist_permissions
    )

    publisher_group.permissions.set(
        publisher_permissions
    )


@receiver(
    post_save,
    sender=CustomUser,
)
def assign_user_group(
    sender,
    instance,
    **kwargs,
):
    """Assign a user to the group matching their role."""

    if instance.is_superuser:
        return

    group_names = {
        CustomUser.READER: "Reader",
        CustomUser.JOURNALIST: "Journalist",
        CustomUser.EDITOR: "Editor",
        CustomUser.PUBLISHER: "Publisher",
    }

    group_name = group_names.get(
        instance.role
    )

    if group_name:
        group, _ = Group.objects.get_or_create(
            name=group_name
        )

        # A user belongs to only the group
        # matching their current role.
        instance.groups.set(
            [group]
        )

    # Subscriptions only apply to Readers.
    if instance.role != CustomUser.READER:
        instance.subscriptions_publishers.clear()
        instance.subscriptions_journalists.clear()


@receiver(
    pre_save,
    sender=Article,
)
def remember_article_status(
    sender,
    instance,
    **kwargs,
):
    """Remember whether an article was already approved."""

    if not instance.pk:
        instance._was_approved = False
        return

    old_article = (
        Article.objects
        .filter(
            pk=instance.pk
        )
        .first()
    )

    if old_article:
        instance._was_approved = (
            old_article.approved
        )
    else:
        instance._was_approved = False


def notify_article_subscribers(
    article_id,
):
    """Notify subscribers when an article is approved."""

    article = Article.objects.get(
        pk=article_id
    )

    # Independent Journalist article.
    if article.author:
        readers = (
            CustomUser.objects
            .filter(
                role=CustomUser.READER,
                subscriptions_journalists=(
                    article.author
                ),
            )
        )

    # Publisher article.
    else:
        readers = (
            CustomUser.objects
            .filter(
                role=CustomUser.READER,
                subscriptions_publishers=(
                    article.publisher
                ),
            )
        )

    email_addresses = list(
        readers
        .exclude(
            email=""
        )
        .values_list(
            "email",
            flat=True,
        )
        .distinct()
    )

    if email_addresses:
        send_mail(
            subject=(
                f"New article: "
                f"{article.title}"
            ),
            message=article.content,
            from_email=None,
            recipient_list=email_addresses,
            fail_silently=True,
        )

    try:
        requests.post(
            settings.APPROVED_ARTICLE_API_URL,
            json={
                "article_id": article.id,
                "title": article.title,
            },
            headers={
                "X-Internal-Key": (
                    settings.INTERNAL_API_KEY
                )
            },
            timeout=5,
        )

    except requests.RequestException as error:
        logger.warning(
            "Approved article API call "
            "failed: %s",
            error,
        )


@receiver(
    post_save,
    sender=Article,
)
def article_approved(
    sender,
    instance,
    created,
    **kwargs,
):
    """Notify subscribers when approval changes to True."""

    was_approved = getattr(
        instance,
        "_was_approved",
        False,
    )

    if (
        instance.approved
        and not was_approved
    ):
        transaction.on_commit(
            lambda: notify_article_subscribers(
                instance.pk
            )
        )