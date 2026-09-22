"""Django admin configuration for the news application.

This module registers the application's custom user, article,
publisher, and newsletter models with the Django administration site.

The admin classes configure how each model is displayed, searched,
filtered, and edited in the Django admin interface.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article
from .models import CustomUser
from .models import Newsletter
from .models import Publisher


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Configure the Django admin interface for custom users.

    This class extends Django's standard
    :class:`django.contrib.auth.admin.UserAdmin` class to include
    fields required by the news application.

    The additional fields allow an administrator to view the user's
    role and Reader subscription information.

    The admin list displays the username, email address, application
    role, and staff status.

    :ivar fieldsets:
        Extends the standard Django user fieldsets with the news
        application role and subscription fields.
    :vartype fieldsets: tuple

    :ivar add_fieldsets:
        Extends the standard user creation form with the application
        role and email address.
    :vartype add_fieldsets: tuple

    :ivar list_display:
        Fields displayed in the Django admin user list.
    :vartype list_display: tuple
    """

    fieldsets = UserAdmin.fieldsets + (
        (
            "News application",
            {
                "fields": (
                    "role",
                    "subscriptions_publishers",
                    "subscriptions_journalists",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "News application",
            {
                "fields": (
                    "role",
                    "email",
                )
            },
        ),
    )

    list_display = (
        "username",
        "email",
        "role",
        "is_staff",
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Configure the Django admin interface for articles.

    This admin configuration determines which Article fields are
    displayed in the article list and provides filtering and search
    functionality.

    Articles can be filtered according to approval status, Publisher,
    and creation date.

    Administrators can search article records using the article title
    or article content.

    :ivar list_display:
        Article fields displayed in the Django admin list view.
    :vartype list_display: tuple

    :ivar list_filter:
        Article fields available as filters in the admin interface.
    :vartype list_filter: tuple

    :ivar search_fields:
        Article fields searched when using the Django admin search
        facility.
    :vartype search_fields: tuple
    """

    list_display = (
        "title",
        "author",
        "publisher",
        "approved",
        "created_at",
    )

    list_filter = (
        "approved",
        "publisher",
        "created_at",
    )

    search_fields = (
        "title",
        "content",
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Configure the Django admin interface for Publishers.

    Publisher records are displayed by name and can be searched by
    their Publisher name.

    The normal application workflow allows Publisher accounts to
    manage their employees through the frontend. The Django admin
    interface is intended primarily for system maintenance.

    :ivar list_display:
        Publisher fields displayed in the Django admin list.
    :vartype list_display: tuple

    :ivar search_fields:
        Publisher fields searched by the Django admin search facility.
    :vartype search_fields: tuple
    """

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Configure the Django admin interface for newsletters.

    The newsletter admin list displays the newsletter title, author,
    and creation date.

    Administrators can search newsletters using the title or
    description.

    :ivar list_display:
        Newsletter fields displayed in the Django admin list view.
    :vartype list_display: tuple

    :ivar search_fields:
        Newsletter fields used when searching from the Django admin
        interface.
    :vartype search_fields: tuple
    """

    list_display = (
        "title",
        "author",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )