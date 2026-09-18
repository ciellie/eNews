from rest_framework.permissions import (
    BasePermission,
)
from rest_framework.permissions import (
    SAFE_METHODS,
)

from .models import CustomUser


class ArticlePermission(
    BasePermission
):
    def has_permission(
        self,
        request,
        view,
    ):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        if request.method == "POST":
            return (
                request.user.role
                == CustomUser.JOURNALIST
            )

        return request.user.role in [
            CustomUser.JOURNALIST,
            CustomUser.EDITOR,
        ]

    def has_object_permission(
        self,
        request,
        view,
        article,
    ):
        if request.method in SAFE_METHODS:
            return True

        if (
            request.user.role
            == CustomUser.EDITOR
        ):
            return True

        if (
            request.user.role
            != CustomUser.JOURNALIST
        ):
            return False

        if article.author:
            return (
                article.author
                == request.user
            )

        if article.publisher:
            return (
                article.publisher
                .journalists
                .filter(
                    pk=request.user.pk
                )
                .exists()
            )

        return False


class IsEditor(
    BasePermission
):
    def has_permission(
        self,
        request,
        view,
    ):
        return (
            request.user.is_authenticated
            and (
                request.user.role
                == CustomUser.EDITOR
                or request.user.groups.filter(
                    name="Editor"
                ).exists()
            )
        )


class IsReader(
    BasePermission
):
    def has_permission(
        self,
        request,
        view,
    ):
        return (
            request.user.is_authenticated
            and request.user.role
            == CustomUser.READER
        )


class NewsletterPermission(
    BasePermission
):
    def has_permission(
        self,
        request,
        view,
    ):
        if not request.user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return request.user.role in [
            CustomUser.JOURNALIST,
            CustomUser.EDITOR,
        ]

    def has_object_permission(
        self,
        request,
        view,
        newsletter,
    ):
        if request.method in SAFE_METHODS:
            return True

        if (
            request.user.role
            == CustomUser.EDITOR
        ):
            return True

        return (
            newsletter.author
            == request.user
        )

    