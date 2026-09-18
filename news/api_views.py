"""REST API views for the news application."""

from django.conf import settings
from django.db.models import Q

from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Article
from .models import CustomUser
from .models import Newsletter
from .models import Publisher

from .permissions import ArticlePermission
from .permissions import IsEditor
from .permissions import IsReader
from .permissions import NewsletterPermission

from .serializers import ArticleSerializer
from .serializers import NewsletterSerializer
from .serializers import PublisherSerializer
from .serializers import UserSerializer


class ArticleViewSet(
    viewsets.ModelViewSet
):
    """API endpoints for articles."""

    serializer_class = ArticleSerializer

    permission_classes = [
        IsAuthenticated,
        ArticlePermission,
    ]

    def get_queryset(self):
        """Return articles based on user role and action."""

        user = self.request.user

        # GET /api/articles/
        # Everyone can only see approved articles
        # in the normal article list.
        if self.action == "list":
            return (
                Article.objects
                .filter(
                    approved=True
                )
                .select_related(
                    "author",
                    "publisher",
                )
                .order_by(
                    "-created_at"
                )
            )

        # Editors may access all articles,
        # including unapproved articles.
        if (
            user.is_superuser
            or user.role
            == CustomUser.EDITOR
            or user.groups.filter(
                name="Editor"
            ).exists()
        ):
            return (
                Article.objects
                .all()
                .select_related(
                    "author",
                    "publisher",
                )
            )

        # Journalists can access approved articles
        # plus their own independent or publisher
        # articles.
        if (
            user.role
            == CustomUser.JOURNALIST
            or user.groups.filter(
                name="Journalist"
            ).exists()
        ):
            return (
                Article.objects
                .filter(
                    Q(
                        approved=True
                    )
                    | Q(
                        author=user
                    )
                    | Q(
                        publisher__journalists=(
                            user
                        )
                    )
                )
                .select_related(
                    "author",
                    "publisher",
                )
                .distinct()
            )

        # Readers can only retrieve
        # approved articles.
        return (
            Article.objects
            .filter(
                approved=True
            )
            .select_related(
                "author",
                "publisher",
            )
        )

    def perform_create(
        self,
        serializer,
    ):
        """Create an unapproved article."""

        publisher = (
            serializer
            .validated_data
            .get(
                "publisher"
            )
        )

        if publisher:
            # Article belongs to a publisher.
            #
            # The serializer checks that
            # the journalist belongs to
            # this publisher.
            serializer.save(
                author=None,
                approved=False,
            )

        else:
            # Independent journalist article.
            serializer.save(
                author=self.request.user,
                approved=False,
            )

    @action(
        detail=False,
        methods=[
            "get",
        ],
        permission_classes=[
            IsAuthenticated,
            IsReader,
        ],
    )
    def subscribed(
        self,
        request,
    ):
        """
        Return approved articles from publishers
        and journalists subscribed to by reader.
        """

        publishers = (
            request.user
            .subscriptions_publishers
            .all()
        )

        journalists = (
            request.user
            .subscriptions_journalists
            .all()
        )

        articles = (
            Article.objects
            .filter(
                approved=True
            )
            .filter(
                Q(
                    publisher__in=(
                        publishers
                    )
                )
                | Q(
                    author__in=(
                        journalists
                    )
                )
            )
            .select_related(
                "author",
                "publisher",
            )
            .distinct()
            .order_by(
                "-created_at"
            )
        )

        serializer = self.get_serializer(
            articles,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=[
            "post",
        ],
        permission_classes=[
            IsAuthenticated,
            IsEditor,
        ],
    )
    def approve(
        self,
        request,
        pk=None,
    ):
        """Allow an editor to approve an article."""

        article = self.get_object()

        if article.approved:
            return Response(
                {
                    "detail": (
                        "Article is already "
                        "approved."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        article.approved = True

        article.save(
            update_fields=[
                "approved",
            ]
        )

        serializer = self.get_serializer(
            article
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


class NewsletterViewSet(
    viewsets.ModelViewSet
):
    """API endpoints for newsletters."""

    queryset = (
        Newsletter.objects
        .select_related(
            "author"
        )
        .prefetch_related(
            "articles"
        )
        .order_by(
            "-created_at"
        )
    )

    serializer_class = (
        NewsletterSerializer
    )

    permission_classes = [
        IsAuthenticated,
        NewsletterPermission,
    ]

    def perform_create(
        self,
        serializer,
    ):
        """Set the current user as newsletter author."""

        serializer.save(
            author=self.request.user
        )


class PublisherViewSet(
    viewsets.ReadOnlyModelViewSet
):
    """Read-only API endpoints for publishers."""

    queryset = (
        Publisher.objects
        .prefetch_related(
            "editors",
            "journalists",
        )
        .order_by(
            "name"
        )
    )

    serializer_class = (
        PublisherSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]


class UserViewSet(
    viewsets.ReadOnlyModelViewSet
):
    """Read-only API endpoints for users."""

    queryset = (
        CustomUser.objects
        .all()
        .order_by(
            "username"
        )
    )

    serializer_class = (
        UserSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]


class ApprovedArticleAPIView(
    APIView
):
    """
    Internal endpoint called when an
    article is approved.

    Access is controlled using the
    X-Internal-Key HTTP header.
    """

    permission_classes = [
        AllowAny,
    ]

    def post(
        self,
        request,
    ):
        """Receive notification of approved article."""

        supplied_key = (
            request.headers.get(
                "X-Internal-Key"
            )
        )

        if (
            supplied_key
            != settings.INTERNAL_API_KEY
        ):
            return Response(
                {
                    "detail": (
                        "Invalid internal key."
                    )
                },
                status=(
                    status.HTTP_403_FORBIDDEN
                ),
            )

        article_id = (
            request.data.get(
                "article_id"
            )
        )

        title = (
            request.data.get(
                "title"
            )
        )

        return Response(
            {
                "received": True,
                "article_id": article_id,
                "title": title,
            },
            status=status.HTTP_200_OK,
        )