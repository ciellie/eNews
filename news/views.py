"""Views for the news application."""

from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from .forms import ArticleForm
from .forms import NewsletterForm
from .forms import PublisherEmployeeForm
from .forms import RegisterForm
from .models import Article
from .models import CustomUser
from .models import Newsletter
from .models import Publisher


# =========================================================
# ROLE HELPERS
# =========================================================


def is_editor(user):
    """Check whether the user is an active Editor."""

    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if user.role != CustomUser.EDITOR:
        return False

    # An Editor must have been assigned
    # to at least one Publisher.
    return (
        user.editor_publishers
        .exists()
    )


def is_journalist(user):
    """Check whether the user is a Journalist."""

    return (
        user.is_authenticated
        and user.role
        == CustomUser.JOURNALIST
    )


def is_publisher(user):
    """Check whether the user is a Publisher."""

    return (
        user.is_authenticated
        and user.role
        == CustomUser.PUBLISHER
    )


# =========================================================
# ROLE DECORATORS
# =========================================================


def editor_required(
    view_function,
):
    """Require active Editor access."""

    @wraps(view_function)
    @login_required
    def wrapper(
        request,
        *args,
        **kwargs,
    ):
        if not is_editor(
            request.user
        ):
            messages.error(
                request,
                (
                    "Active Editor access "
                    "required."
                ),
            )

            return redirect(
                "home"
            )

        return view_function(
            request,
            *args,
            **kwargs,
        )

    return wrapper


def journalist_required(
    view_function,
):
    """Require Journalist access."""

    @wraps(view_function)
    @login_required
    def wrapper(
        request,
        *args,
        **kwargs,
    ):
        if not is_journalist(
            request.user
        ):
            messages.error(
                request,
                (
                    "Journalist access "
                    "required."
                ),
            )

            return redirect(
                "home"
            )

        return view_function(
            request,
            *args,
            **kwargs,
        )

    return wrapper


def publisher_required(
    view_function,
):
    """Require Publisher access."""

    @wraps(view_function)
    @login_required
    def wrapper(
        request,
        *args,
        **kwargs,
    ):
        if not is_publisher(
            request.user
        ):
            messages.error(
                request,
                (
                    "Publisher access "
                    "required."
                ),
            )

            return redirect(
                "home"
            )

        return view_function(
            request,
            *args,
            **kwargs,
        )

    return wrapper


# =========================================================
# PERMISSION HELPERS
# =========================================================


def can_manage_article(
    user,
    article,
):
    """Check whether user may edit/delete an article."""

    if user.is_superuser:
        return True

    # Editors may manage independent articles.
    # For Publisher articles they must work
    # for that Publisher.
    if is_editor(user):

        if article.publisher:
            return (
                article.publisher
                .editors
                .filter(
                    pk=user.pk
                )
                .exists()
            )

        return True

    if not is_journalist(user):
        return False

    # Independent Journalist article.
    if article.author:
        return (
            article.author_id
            == user.pk
        )

    # Publisher article.
    if article.publisher:
        return (
            article.publisher
            .journalists
            .filter(
                pk=user.pk
            )
            .exists()
        )

    return False


def can_approve_article(
    user,
    article,
):
    """Check whether Editor may approve an article."""

    if user.is_superuser:
        return True

    if not is_editor(user):
        return False

    # Publisher article:
    # Editor must belong to this Publisher.
    if article.publisher:
        return (
            article.publisher
            .editors
            .filter(
                pk=user.pk
            )
            .exists()
        )

    # Independent articles may be approved
    # by any active Editor.
    return True


def can_manage_newsletter(
    user,
    newsletter,
):
    """Check whether user may edit/delete a newsletter."""

    if user.is_superuser:
        return True

    if is_editor(user):
        return True

    if is_journalist(user):
        return (
            newsletter.author_id
            == user.pk
        )

    return False


# =========================================================
# HOME
# =========================================================


def home(request):
    """Display articles appropriate for the current user."""

    articles = (
        Article.objects
        .filter(
            approved=True
        )
        .select_related(
            "author",
            "publisher",
        )
    )

    # Logged-in Readers only see approved
    # articles from their subscriptions.
    if (
        request.user.is_authenticated
        and request.user.role
        == CustomUser.READER
    ):
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
            articles
            .filter(
                Q(
                    publisher__in=publishers
                )
                |
                Q(
                    author__in=journalists
                )
            )
            .distinct()
        )

    articles = articles.order_by(
        "-created_at"
    )

    return render(
        request,
        "news/home.html",
        {
            "articles": articles,
        },
    )


# =========================================================
# REGISTRATION
# =========================================================


def register(request):
    """Register a new application user."""

    if request.user.is_authenticated:
        return redirect(
            "home"
        )

    if request.method == "POST":
        form = RegisterForm(
            request.POST
        )

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
            )

            messages.success(
                request,
                (
                    "Your account has "
                    "been created."
                ),
            )

            return redirect(
                "home"
            )

    else:
        form = RegisterForm()

    return render(
        request,
        "news/register.html",
        {
            "form": form,
        },
    )


# =========================================================
# JOURNALIST ARTICLES
# =========================================================


@journalist_required
def journalist_articles(request):
    """Display articles manageable by Journalist."""

    articles = (
        Article.objects
        .filter(
            Q(
                author=request.user
            )
            |
            Q(
                publisher__journalists=(
                    request.user
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

    return render(
        request,
        "news/journalist_articles.html",
        {
            "articles": articles,
        },
    )


@journalist_required
def article_create(request):
    """Allow a Journalist to create an article."""

    if request.method == "POST":
        form = ArticleForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            article = form.save(
                commit=False
            )

            # Publisher article.
            if article.publisher:
                article.author = None

            # Independent article.
            else:
                article.author = (
                    request.user
                )

            # Journalists cannot approve
            # their own articles.
            article.approved = False

            article.save()

            messages.success(
                request,
                (
                    "Article created and sent "
                    "for Editor approval."
                ),
            )

            return redirect(
                "journalist_articles"
            )

    else:
        form = ArticleForm(
            user=request.user
        )

    return render(
        request,
        "news/article_form.html",
        {
            "form": form,
            "page_title": (
                "Create Article"
            ),
        },
    )


@login_required
def article_edit(
    request,
    article_id,
):
    """Edit an article."""

    article = get_object_or_404(
        Article,
        pk=article_id,
    )

    if not can_manage_article(
        request.user,
        article,
    ):
        messages.error(
            request,
            (
                "You may not edit "
                "this article."
            ),
        )

        return redirect(
            "home"
        )

    if request.method == "POST":
        form = ArticleForm(
            request.POST,
            instance=article,
            user=request.user,
        )

        if form.is_valid():
            edited_article = form.save(
                commit=False
            )

            if is_journalist(
                request.user
            ):
                if edited_article.publisher:
                    edited_article.author = None

                else:
                    edited_article.author = (
                        request.user
                    )

            edited_article.save()

            messages.success(
                request,
                "Article updated.",
            )

            if is_editor(
                request.user
            ):
                return redirect(
                    "editor_review"
                )

            return redirect(
                "journalist_articles"
            )

    else:
        form = ArticleForm(
            instance=article,
            user=request.user,
        )

    return render(
        request,
        "news/article_form.html",
        {
            "form": form,
            "page_title": (
                "Edit Article"
            ),
            "article": article,
        },
    )


@login_required
def article_delete(
    request,
    article_id,
):
    """Delete an article."""

    article = get_object_or_404(
        Article,
        pk=article_id,
    )

    if not can_manage_article(
        request.user,
        article,
    ):
        messages.error(
            request,
            (
                "You may not delete "
                "this article."
            ),
        )

        return redirect(
            "home"
        )

    if request.method == "POST":
        article.delete()

        messages.success(
            request,
            "Article deleted.",
        )

        if is_editor(
            request.user
        ):
            return redirect(
                "editor_review"
            )

        return redirect(
            "journalist_articles"
        )

    return render(
        request,
        "news/article_confirm_delete.html",
        {
            "article": article,
        },
    )


# =========================================================
# EDITOR ARTICLE REVIEW
# =========================================================


@editor_required
def editor_review(request):
    """Display articles the Editor may review."""

    # Superuser may review everything.
    if request.user.is_superuser:
        articles = (
            Article.objects
            .filter(
                approved=False
            )
            .select_related(
                "author",
                "publisher",
            )
            .order_by(
                "created_at"
            )
        )

    else:
        publisher_ids = (
            request.user
            .editor_publishers
            .values_list(
                "id",
                flat=True,
            )
        )

        articles = (
            Article.objects
            .filter(
                approved=False
            )
            .filter(
                Q(
                    publisher_id__in=(
                        publisher_ids
                    )
                )
                |
                Q(
                    publisher__isnull=True
                )
            )
            .select_related(
                "author",
                "publisher",
            )
            .distinct()
            .order_by(
                "created_at"
            )
        )

    return render(
        request,
        "news/editor_review.html",
        {
            "articles": articles,
        },
    )


@editor_required
def approve_article(
    request,
    article_id,
):
    """Approve an article."""

    article = get_object_or_404(
        Article,
        pk=article_id,
    )

    if not can_approve_article(
        request.user,
        article,
    ):
        messages.error(
            request,
            (
                "You are not permitted "
                "to approve this article."
            ),
        )

        return redirect(
            "editor_review"
        )

    if request.method != "POST":
        return redirect(
            "editor_review"
        )

    if article.approved:
        messages.info(
            request,
            (
                "This article is already "
                "approved."
            ),
        )

        return redirect(
            "editor_review"
        )

    article.approved = True

    article.save(
        update_fields=[
            "approved",
        ]
    )

    messages.success(
        request,
        "Article approved.",
    )

    return redirect(
        "editor_review"
    )


# =========================================================
# READER SUBSCRIPTIONS
# =========================================================


@login_required
def subscriptions(request):
    """Allow Readers to manage subscriptions."""

    if (
        request.user.role
        != CustomUser.READER
    ):
        messages.error(
            request,
            "Reader access required.",
        )

        return redirect(
            "home"
        )

    publishers = (
        Publisher.objects
        .all()
        .order_by(
            "name"
        )
    )

    journalists = (
        CustomUser.objects
        .filter(
            role=CustomUser.JOURNALIST
        )
        .order_by(
            "username"
        )
    )

    return render(
        request,
        "news/subscriptions.html",
        {
            "publishers": publishers,
            "journalists": journalists,
        },
    )


@login_required
def toggle_publisher_subscription(
    request,
    publisher_id,
):
    """Subscribe or unsubscribe from a Publisher."""

    if (
        request.user.role
        != CustomUser.READER
    ):
        return redirect(
            "home"
        )

    publisher = get_object_or_404(
        Publisher,
        pk=publisher_id,
    )

    if request.method == "POST":

        if (
            request.user
            .subscriptions_publishers
            .filter(
                pk=publisher.pk
            )
            .exists()
        ):
            (
                request.user
                .subscriptions_publishers
                .remove(
                    publisher
                )
            )

            messages.success(
                request,
                "Publisher unsubscribed.",
            )

        else:
            (
                request.user
                .subscriptions_publishers
                .add(
                    publisher
                )
            )

            messages.success(
                request,
                "Publisher subscribed.",
            )

    return redirect(
        "subscriptions"
    )


@login_required
def toggle_journalist_subscription(
    request,
    journalist_id,
):
    """Subscribe or unsubscribe from a Journalist."""

    if (
        request.user.role
        != CustomUser.READER
    ):
        return redirect(
            "home"
        )

    journalist = get_object_or_404(
        CustomUser,
        pk=journalist_id,
        role=CustomUser.JOURNALIST,
    )

    if request.method == "POST":

        if (
            request.user
            .subscriptions_journalists
            .filter(
                pk=journalist.pk
            )
            .exists()
        ):
            (
                request.user
                .subscriptions_journalists
                .remove(
                    journalist
                )
            )

            messages.success(
                request,
                "Journalist unsubscribed.",
            )

        else:
            (
                request.user
                .subscriptions_journalists
                .add(
                    journalist
                )
            )

            messages.success(
                request,
                "Journalist subscribed.",
            )

    return redirect(
        "subscriptions"
    )


# =========================================================
# NEWSLETTERS
# =========================================================


@login_required
def newsletter_list(request):
    """Display newsletters."""

    newsletters = (
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

    return render(
        request,
        "news/newsletter_list.html",
        {
            "newsletters": newsletters,
        },
    )


@journalist_required
def newsletter_create(request):
    """Allow a Journalist to create a newsletter."""

    if request.method == "POST":
        form = NewsletterForm(
            request.POST,
            user=request.user,
        )

        if form.is_valid():
            newsletter = form.save(
                commit=False
            )

            newsletter.author = (
                request.user
            )

            newsletter.save()

            form.save_m2m()

            messages.success(
                request,
                "Newsletter created.",
            )

            return redirect(
                "newsletter_list"
            )

    else:
        form = NewsletterForm(
            user=request.user
        )

    return render(
        request,
        "news/newsletter_form.html",
        {
            "form": form,
            "page_title": (
                "Create Newsletter"
            ),
        },
    )


@login_required
def newsletter_edit(
    request,
    newsletter_id,
):
    """Edit a newsletter."""

    newsletter = get_object_or_404(
        Newsletter,
        pk=newsletter_id,
    )

    if not can_manage_newsletter(
        request.user,
        newsletter,
    ):
        messages.error(
            request,
            (
                "You may not edit "
                "this newsletter."
            ),
        )

        return redirect(
            "newsletter_list"
        )

    if request.method == "POST":
        form = NewsletterForm(
            request.POST,
            instance=newsletter,
            user=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Newsletter updated.",
            )

            return redirect(
                "newsletter_list"
            )

    else:
        form = NewsletterForm(
            instance=newsletter,
            user=request.user,
        )

    return render(
        request,
        "news/newsletter_form.html",
        {
            "form": form,
            "page_title": (
                "Edit Newsletter"
            ),
            "newsletter": newsletter,
        },
    )


@login_required
def newsletter_delete(
    request,
    newsletter_id,
):
    """Delete a newsletter."""

    newsletter = get_object_or_404(
        Newsletter,
        pk=newsletter_id,
    )

    if not can_manage_newsletter(
        request.user,
        newsletter,
    ):
        messages.error(
            request,
            (
                "You may not delete "
                "this newsletter."
            ),
        )

        return redirect(
            "newsletter_list"
        )

    if request.method == "POST":
        newsletter.delete()

        messages.success(
            request,
            "Newsletter deleted.",
        )

        return redirect(
            "newsletter_list"
        )

    return render(
        request,
        "news/newsletter_confirm_delete.html",
        {
            "newsletter": newsletter,
        },
    )


# =========================================================
# PUBLISHER PROFILE
# =========================================================


@publisher_required
def publisher_dashboard(request):
    """Display the Publisher profile."""

    publisher, created = (
        Publisher.objects.get_or_create(
            owner=request.user,
            defaults={
                "name": request.user.username,
                "description": "",
            },
        )
    )

    return render(
        request,
        "news/publisher_dashboard.html",
        {
            "publisher": publisher,
        },
    )

# =========================================================
# PUBLISHER EMPLOYEES
# =========================================================


@publisher_required
def publisher_employees(request):
    """Manage Publisher employees."""

    publisher, created = (
        Publisher.objects.get_or_create(
            owner=request.user,
            defaults={
                "name": request.user.username,
                "description": "",
            },
        )
    )

    if request.method == "POST":
        form = PublisherEmployeeForm(
            request.POST
        )

        if form.is_valid():
            employee = (
                form.cleaned_data[
                    "user"
                ]
            )

            employee_type = (
                form.cleaned_data[
                    "employee_type"
                ]
            )

            if (
                employee_type
                == CustomUser.JOURNALIST
            ):
                publisher.journalists.add(
                    employee
                )

                messages.success(
                    request,
                    (
                        f"{employee.username} "
                        "was added as a "
                        "Journalist."
                    ),
                )

            elif (
                employee_type
                == CustomUser.EDITOR
            ):
                publisher.editors.add(
                    employee
                )

                messages.success(
                    request,
                    (
                        f"{employee.username} "
                        "was added as an "
                        "Editor."
                    ),
                )

            return redirect(
                "publisher_employees"
            )

    else:
        form = PublisherEmployeeForm()

    return render(
        request,
        "news/publisher_employees.html",
        {
            "publisher": publisher,
            "form": form,
        },
    )


@publisher_required
def remove_publisher_employee(
    request,
    user_id,
    employee_type,
):
    """Remove an employee from a Publisher."""

    publisher = get_object_or_404(
        Publisher,
        owner=request.user,
    )

    employee = get_object_or_404(
        CustomUser,
        pk=user_id,
    )

    if request.method != "POST":
        return redirect(
            "publisher_employees"
        )

    if employee_type == "journalist":
        publisher.journalists.remove(
            employee
        )

        messages.success(
            request,
            (
                f"{employee.username} "
                "was removed as a "
                "Journalist."
            ),
        )

    elif employee_type == "editor":
        publisher.editors.remove(
            employee
        )

        messages.success(
            request,
            (
                f"{employee.username} "
                "was removed as an "
                "Editor."
            ),
        )

    else:
        messages.error(
            request,
            "Invalid employee type.",
        )

    return redirect(
        "publisher_employees"
    )