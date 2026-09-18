"""Admin configuration for the news application."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article
from .models import CustomUser
from .models import Newsletter
from .models import Publisher


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for custom users."""

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
    """Admin configuration for articles."""

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
    """Admin configuration for publishers."""

    list_display = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """Admin configuration for newsletters."""

    list_display = (
        "title",
        "author",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )