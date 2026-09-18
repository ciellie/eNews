"""Automated tests for the news REST API."""

from unittest.mock import patch

from django.test import TestCase

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Article
from .models import CustomUser
from .models import Newsletter
from .models import Publisher


class NewsAPITests(TestCase):
    """Test authentication, permissions, and API behaviour."""

    def setUp(self):
        """Create test users and news content."""

        self.client = APIClient()

        self.reader = (
            CustomUser.objects.create_user(
                username="reader",
                email="reader@example.com",
                password="Test12345",
                role=CustomUser.READER,
            )
        )

        self.journalist1 = (
            CustomUser.objects.create_user(
                username="journalist1",
                email="j1@example.com",
                password="Test12345",
                role=CustomUser.JOURNALIST,
            )
        )

        self.journalist2 = (
            CustomUser.objects.create_user(
                username="journalist2",
                email="j2@example.com",
                password="Test12345",
                role=CustomUser.JOURNALIST,
            )
        )

        self.editor = (
            CustomUser.objects.create_user(
                username="editor",
                email="editor@example.com",
                password="Test12345",
                role=CustomUser.EDITOR,
            )
        )

        self.publisher1 = (
            Publisher.objects.create(
                name="Publisher One"
            )
        )

        self.publisher2 = (
            Publisher.objects.create(
                name="Publisher Two"
            )
        )

        self.publisher1.journalists.add(
            self.journalist1
        )

        self.publisher2.journalists.add(
            self.journalist2
        )

        self.publisher1.editors.add(
            self.editor
        )

        self.reader.subscriptions_publishers.add(
            self.publisher1
        )

        self.reader.subscriptions_journalists.add(
            self.journalist1
        )

        self.article1 = Article.objects.create(
            title="Journalist One Article",
            content="Article content",
            author=self.journalist1,
            approved=True,
        )

        self.article2 = Article.objects.create(
            title="Journalist Two Article",
            content="Other content",
            author=self.journalist2,
            approved=True,
        )

        self.publisher_article = (
            Article.objects.create(
                title="Publisher One Article",
                content="Publisher content",
                publisher=self.publisher1,
                approved=True,
            )
        )

        self.unapproved_article = (
            Article.objects.create(
                title="Waiting Article",
                content="Waiting for approval",
                author=self.journalist1,
                approved=False,
            )
        )

    def authenticate(self, user):
        """Authenticate API client using token authentication."""

        token, _ = (
            Token.objects.get_or_create(
                user=user
            )
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Token {token.key}"
            )
        )

    def test_unauthenticated_user_cannot_access_articles(
        self,
    ):
        """Anonymous API access should fail."""

        response = self.client.get(
            "/api/articles/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_reader_can_view_approved_articles(self):
        """Reader should retrieve approved articles."""

        self.authenticate(
            self.reader
        )

        response = self.client.get(
            "/api/articles/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            item["title"]
            for item in response.data
        ]

        self.assertIn(
            "Journalist One Article",
            titles,
        )

        self.assertIn(
            "Journalist Two Article",
            titles,
        )

        self.assertIn(
            "Publisher One Article",
            titles,
        )

        self.assertNotIn(
            "Waiting Article",
            titles,
        )

    def test_reader_gets_only_subscribed_articles(
        self,
    ):
        """Reader subscribed endpoint should filter content."""

        self.authenticate(
            self.reader
        )

        response = self.client.get(
            "/api/articles/subscribed/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        titles = [
            item["title"]
            for item in response.data
        ]

        self.assertIn(
            "Journalist One Article",
            titles,
        )

        self.assertIn(
            "Publisher One Article",
            titles,
        )

        self.assertNotIn(
            "Journalist Two Article",
            titles,
        )

    def test_journalist_cannot_use_subscribed_endpoint(
        self,
    ):
        """Subscribed endpoint should be reader only."""

        self.authenticate(
            self.journalist1
        )

        response = self.client.get(
            "/api/articles/subscribed/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_journalist_can_create_article(self):
        """Journalist should be able to create an article."""

        self.authenticate(
            self.journalist1
        )

        response = self.client.post(
            "/api/articles/",
            {
                "title": "New Article",
                "content": "New content",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        article = Article.objects.get(
            title="New Article"
        )

        self.assertEqual(
            article.author,
            self.journalist1,
        )

        self.assertFalse(
            article.approved
        )

    def test_reader_cannot_create_article(self):
        """Reader should not be able to create an article."""

        self.authenticate(
            self.reader
        )

        response = self.client.post(
            "/api/articles/",
            {
                "title": "Illegal Article",
                "content": "Should fail",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_editor_cannot_create_article(self):
        """Only journalists should create articles."""

        self.authenticate(
            self.editor
        )

        response = self.client.post(
            "/api/articles/",
            {
                "title": "Editor Article",
                "content": "Should fail",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_journalist_can_update_own_article(self):
        """Journalist can update their own article."""

        self.authenticate(
            self.journalist1
        )

        response = self.client.patch(
            f"/api/articles/{self.article1.id}/",
            {
                "title": "Updated Article",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.article1.refresh_from_db()

        self.assertEqual(
            self.article1.title,
            "Updated Article",
        )

    def test_journalist_cannot_update_other_article(
        self,
    ):
        """Journalists should not modify another journalist's article."""

        self.authenticate(
            self.journalist1
        )

        response = self.client.patch(
            f"/api/articles/{self.article2.id}/",
            {
                "title": "Illegal Update",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_journalist_cannot_approve_article(self):
        """Journalists must not approve articles."""

        self.authenticate(
            self.journalist1
        )

        response = self.client.post(
            (
                f"/api/articles/"
                f"{self.unapproved_article.id}/"
                "approve/"
            )
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.unapproved_article.refresh_from_db()

        self.assertFalse(
            self.unapproved_article.approved
        )

    @patch(
        "news.signals.requests.post"
    )
    @patch(
        "news.signals.send_mail"
    )
    def test_editor_can_approve_article(
        self,
        mock_email,
        mock_post,
    ):
        """Editor should approve an article."""

        self.authenticate(
            self.editor
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            response = self.client.post(
                (
                    f"/api/articles/"
                    f"{self.unapproved_article.id}/"
                    "approve/"
                )
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.unapproved_article.refresh_from_db()

        self.assertTrue(
            self.unapproved_article.approved
        )

        mock_email.assert_called_once()

        mock_post.assert_called_once()

    def test_editor_can_delete_article(self):
        """Editor should be able to delete an article."""

        article = Article.objects.create(
            title="Delete Me",
            content="Delete content",
            author=self.journalist1,
            approved=False,
        )

        self.authenticate(
            self.editor
        )

        response = self.client.delete(
            f"/api/articles/{article.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Article.objects.filter(
                pk=article.id
            ).exists()
        )

    def test_reader_cannot_delete_article(self):
        """Reader should not be able to delete articles."""

        self.authenticate(
            self.reader
        )

        response = self.client.delete(
            f"/api/articles/{self.article1.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Article.objects.filter(
                pk=self.article1.id
            ).exists()
        )

    def test_journalist_can_create_newsletter(self):
        """Journalist should be able to create newsletter."""

        self.authenticate(
            self.journalist1
        )

        response = self.client.post(
            "/api/newsletters/",
            {
                "title": "Weekly News",
                "description": (
                    "Weekly newsletter"
                ),
                "articles": [
                    self.article1.id,
                    self.publisher_article.id,
                ],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        newsletter = (
            Newsletter.objects.get(
                title="Weekly News"
            )
        )

        self.assertEqual(
            newsletter.author,
            self.journalist1,
        )

        self.assertEqual(
            newsletter.articles.count(),
            2,
        )

    def test_reader_cannot_create_newsletter(self):
        """Reader should not create newsletters."""

        self.authenticate(
            self.reader
        )

        response = self.client.post(
            "/api/newsletters/",
            {
                "title": "Reader Newsletter",
                "description": "Should fail",
                "articles": [
                    self.article1.id
                ],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_editor_can_delete_newsletter(self):
        """Editor can delete a journalist newsletter."""

        newsletter = Newsletter.objects.create(
            title="Delete Newsletter",
            description="Test",
            author=self.journalist1,
        )

        newsletter.articles.add(
            self.article1
        )

        self.authenticate(
            self.editor
        )

        response = self.client.delete(
            f"/api/newsletters/{newsletter.id}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Newsletter.objects.filter(
                pk=newsletter.id
            ).exists()
        )

    @patch(
        "news.signals.requests.post"
    )
    @patch(
        "news.signals.send_mail"
    )
    def test_approval_signal(
        self,
        mock_email,
        mock_post,
    ):
        """Approval should email and call internal API."""

        article = Article.objects.create(
            title="Signal Article",
            content="Signal test",
            author=self.journalist1,
            approved=False,
        )

        with self.captureOnCommitCallbacks(
            execute=True
        ):
            article.approved = True
            article.save()

        mock_email.assert_called_once()

        mock_post.assert_called_once()

        called_url = (
            mock_post.call_args.args[0]
        )

        self.assertIn(
            "/api/approved/",
            called_url,
        )