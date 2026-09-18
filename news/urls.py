from django.urls import path

from . import views


urlpatterns = [
    path(
        "",
        views.home,
        name="home",
    ),

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "journalist/articles/",
        views.journalist_articles,
        name="journalist_articles",
    ),

    path(
        "articles/create/",
        views.article_create,
        name="article_create",
    ),

    path(
        "articles/<int:article_id>/edit/",
        views.article_edit,
        name="article_edit",
    ),

    path(
        "articles/<int:article_id>/delete/",
        views.article_delete,
        name="article_delete",
    ),

    path(
        "editor/review/",
        views.editor_review,
        name="editor_review",
    ),

    path(
        "editor/approve/<int:article_id>/",
        views.approve_article,
        name="approve_article",
    ),
    path(
    "subscriptions/",
    views.subscriptions,
    name="subscriptions",
),

    path(
     "subscriptions/publisher/<int:publisher_id>/",
     views.toggle_publisher_subscription,
     name="toggle_publisher_subscription",
),

    path(
     "subscriptions/journalist/<int:journalist_id>/",
     views.toggle_journalist_subscription,
     name="toggle_journalist_subscription",
    ),

     path(
       "newsletters/",
       views.newsletter_list,
       name="newsletter_list",
    ),

     path(
        "newsletters/create/",
        views.newsletter_create,
        name="newsletter_create",
    ),

    path(
        "newsletters/<int:newsletter_id>/edit/",
        views.newsletter_edit,
        name="newsletter_edit",
    ),

    path(
        "newsletters/<int:newsletter_id>/delete/",
        views.newsletter_delete,
        name="newsletter_delete",
    ),

    path(
    "publisher/",
    views.publisher_dashboard,
    name="publisher_dashboard",
     ),

    path(
       "publisher/employees/",
       views.publisher_employees,
       name="publisher_employees",
    ),

    path(
        (
            "publisher/employees/"
            "<int:user_id>/"
            "<str:employee_type>/remove/"
        ),
       views.remove_publisher_employee,
       name="remove_publisher_employee",
    ),
]