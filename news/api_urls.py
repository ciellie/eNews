"""URL configuration for the news REST API."""

from django.urls import path

from rest_framework.authtoken.views import (
    obtain_auth_token,
)
from rest_framework.routers import DefaultRouter

from .api_views import ApprovedArticleAPIView
from .api_views import ArticleViewSet
from .api_views import NewsletterViewSet
from .api_views import PublisherViewSet
from .api_views import UserViewSet


router = DefaultRouter()

router.register(
    "articles",
    ArticleViewSet,
    basename="article",
)

router.register(
    "newsletters",
    NewsletterViewSet,
    basename="newsletter",
)

router.register(
    "publishers",
    PublisherViewSet,
    basename="publisher",
)

router.register(
    "users",
    UserViewSet,
    basename="user",
)


urlpatterns = [
    path(
        "token/",
        obtain_auth_token,
        name="api-token",
    ),

    path(
        "approved/",
        ApprovedArticleAPIView.as_view(),
        name="approved-api",
    ),
]


urlpatterns += router.urls
