# eNewsApp

eNewsApp is a Django-based news application with role-based access for **Readers, Journalists, Editors, and Publishers**.

The application includes:

- user registration and login
- role-based access control
- Publisher profiles
- Publisher employee management
- article creation, editing, deletion, and approval
- independent Journalist articles
- Publisher articles
- newsletters
- Reader subscriptions
- Django REST Framework API endpoints
- token authentication
- email notifications
- Django signals
- MySQL support
- automated tests
- a simple HTML/CSS frontend

---

# 1. Project Overview

The application models a small news-publishing environment.

There are four main application roles:

| Role | Main purpose |
|---|---|
| Reader | Reads approved content and subscribes to Publishers and Journalists |
| Journalist | Creates articles and newsletters |
| Editor | Reviews and approves content when assigned to a Publisher |
| Publisher | Acts as an employer and manages its Journalists and Editors |

The **Publisher role is important** because it controls which Editors and Journalists may act on behalf of a Publisher.

---

# 2. Clone the Project from GitHub

A new user should first clone the project from GitHub.

Open PowerShell or a terminal and run:

```powershell
git clone https://github.com/ciellie/eNews.git
```

Enter the cloned project directory:

```powershell
cd YOUR-REPOSITORY
```

Check that the project files are present:

```powershell
dir
```

You should see files such as:

```text
manage.py
requirements.txt
README.md
```

> The virtual environment should only be created **after entering the cloned project directory**.

---

# 3. Create a Virtual Environment

From inside the project folder:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate the environment again:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

# 4. Install the Dependencies

Make sure you are still in the folder containing `requirements.txt`.

Run:

```powershell
pip install -r requirements.txt
```

Typical project dependencies include:

```text
Django
djangorestframework
mysqlclient
requests
```

---

# 5. Create the MySQL Database

Open MySQL:

```powershell
mysql -u root -p
```

Enter the MySQL root password.

Create the database:

```sql
CREATE DATABASE enewsapp
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Confirm that it exists:

```sql
SHOW DATABASES;
```

Exit MySQL:

```sql
EXIT;
```

---

# 6. Configure the Database Connection

Open:

```text
eNewsApp/settings.py
```

Configure the database:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "enewsapp",
        "USER": "root",
        "PASSWORD": "YOUR_MYSQL_PASSWORD",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
```

Replace `YOUR_MYSQL_PASSWORD` with the password for the local MySQL installation.

> Do not publish real production passwords, Django secret keys, or API keys.

---

# 7. Apply Migrations

The project migrations are included in the repository.

Run:

```powershell
python manage.py migrate
```

`makemigrations` is only required when the models are changed during development.

---

# 8. Create the Default Assessment Administrator

The project includes a management command that creates a temporary Administrator account.

Run:

```powershell
python manage.py create_default_admin
```

Temporary assessment credentials:

| Field | Value |
|---|---|
| Username | `examiner_admin` |
| Email | `examiner@example.com` |
| Password | `ChangeMeNow!2026` |

> **The temporary Administrator password must be changed immediately after the first login.**

The Django Administrator is intended for **system maintenance only** and not for normal application functionality.

---

# 9. Run the Application

Start the development server:

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Login page:

```text
http://127.0.0.1:8000/accounts/login/
```

Registration page:

```text
http://127.0.0.1:8000/register/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

Stop the server with `Ctrl+C`.

---

# 10. User Registration

Users register through the normal application registration page.

Supported account types are:

- Reader
- Journalist
- Editor
- Publisher

Editors are allowed to register, but **registration alone does not give an Editor Publisher approval privileges**.

A Publisher must add the Editor as an employee before that Editor may approve Publisher content.

---

# 11. Publisher Role

The **Publisher** role acts like an employer.

A Publisher account has its own Publisher profile.

The Publisher manages its own employees through the application frontend.

A Publisher can add registered users as:

- Journalists
- Editors

A Publisher may also remove those employees later.

The Publisher does **not** create employee passwords. Journalists and Editors register their own accounts first.

## Publisher workflow

```text
Publisher registers
        ↓
Publisher profile is created
        ↓
Journalist or Editor registers
        ↓
Publisher opens Employees
        ↓
Publisher adds the registered user
        ↓
That user may now act for the Publisher
```

## Publisher responsibilities

A Publisher can:

- view its own Publisher profile
- view its employee list
- add registered Journalists
- add registered Editors
- remove Journalists
- remove Editors

A Publisher may only manage employees belonging to its own Publisher profile.

## Publisher routes

Publisher dashboard:

```text
/publisher/
```

Manage employees:

```text
/publisher/employees/
```

---

# 12. Journalist Role

A Journalist can:

- log in
- create independent articles
- edit their own independent articles
- delete their own independent articles
- create newsletters
- edit their own newsletters
- delete their own newsletters

A Journalist may create a Publisher article **only if that Publisher has added the Journalist as an employee**.

A Journalist cannot approve an article.

---

# 13. Editor Role

An Editor can register through the normal registration page.

However, a newly registered Editor is **not yet an active Publisher Editor**.

To become active:

```text
Editor registers
        ↓
Publisher logs in
        ↓
Publisher adds Editor as employee
        ↓
Editor becomes active for that Publisher
```

For a Publisher article:

- the Editor must be assigned to that Publisher
- the Editor may then review and approve that Publisher's article

An Editor cannot simply register and approve Publisher content without being assigned first.

For independent Journalist articles, an active Editor may review and approve the article.

---

# 14. Reader Role

A Reader can:

- log in
- view newsletters
- subscribe to Publishers
- subscribe to Journalists
- view approved articles from their subscriptions
- use the subscribed-articles API endpoint

Readers do not subscribe directly to newsletters.

When logged in, a Reader sees approved articles only from subscribed Publishers or Journalists.

---

# 15. Public Visitors

A visitor who is not logged in can:

- view all approved articles
- register
- log in

This means the public landing page remains useful even before authentication.

---

# 16. Article Rules

The Article model includes:

- `title`
- `content`
- `author`
- `created_at`
- `approved`
- `publisher`

An article belongs to either:

- an independent Journalist, or
- a Publisher

It must not belong to both at the same time.

New articles are created with:

```text
approved = False
```

---

# 17. Independent Journalist Articles

If the Journalist leaves the Publisher field blank:

```text
author = logged-in Journalist
publisher = None
approved = False
```

The logged-in Journalist becomes the author automatically.

The user does not manually choose the Author.

---

# 18. Publisher Articles

If the Journalist chooses a Publisher:

```text
author = None
publisher = selected Publisher
approved = False
```

The Journalist may only choose a Publisher that employs them.

---

# 19. Article Approval Workflow

For Publisher content:

```text
Journalist registers
        ↓
Publisher adds Journalist
        ↓
Journalist creates Publisher article
        ↓
approved = False
        ↓
Editor registers
        ↓
Publisher adds Editor
        ↓
Editor reviews Publisher article
        ↓
Editor approves article
        ↓
Subscribers are notified
```

Only an eligible Editor may approve the article.

A Journalist cannot approve their own article.

---

# 20. Article Management

## Journalist

A Journalist may:

- create articles
- edit articles they are allowed to manage
- delete articles they are allowed to manage

## Editor

An active Editor may:

- review permitted articles
- edit permitted articles
- delete permitted articles
- approve permitted articles

For Publisher content, the Editor must belong to the relevant Publisher.

---

# 21. Newsletter Functionality

A Newsletter contains:

- `title`
- `description`
- `created_at`
- `author`
- a many-to-many relationship with Articles

## Journalist

A Journalist can:

- create newsletters
- edit their own newsletters
- delete their own newsletters

## Editor

An active Editor can manage newsletters according to the application's permissions.

## Reader

A Reader can view newsletters.

Frontend newsletter page:

```text
/newsletters/
```

---

# 22. Reader Subscriptions

Readers can subscribe to:

- Publishers
- Journalists

Reader subscription page:

```text
/subscriptions/
```

The Reader's homepage is filtered to approved articles from those subscriptions.

---

# 23. Django Groups

The application uses Django Groups for role-based permissions.

Groups include:

- Reader
- Journalist
- Editor
- Publisher

The Publisher group does not automatically receive Editor permissions.

Publisher employee relationships are stored separately and are checked by the application.

---

# 24. Permission Design

The application uses more than just visible menu links.

Protected actions are checked on the server.

Examples include:

- Journalist article ownership
- Publisher membership
- Editor Publisher membership
- Reader-only subscription actions
- Publisher-only employee management
- Editor-only approval

This prevents users from bypassing restrictions by manually entering URLs.

---

# 25. Email Notification on Approval

When an article changes from `approved = False` to `approved = True`, a Django signal is triggered.

For an independent Journalist article, subscribed Readers are found through `subscriptions_journalists`.

For a Publisher article, subscribed Readers are found through `subscriptions_publishers`.

Notification emails are then sent to Readers who have email addresses.

---

# 26. Internal Approval API Notification

After approval, the application also sends a POST request to:

```text
/api/approved/
```

The request includes the article ID and title and uses the `X-Internal-Key` header.

---

# 27. REST API Authentication

The API uses Django REST Framework Token Authentication.

Obtain a token:

```powershell
$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/token/" `
    -Method POST `
    -Body @{
        username = "reader"
        password = "YOUR_PASSWORD"
    }

$token = $response.token
```

Use the token:

```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/articles/" `
    -Headers @{
        Authorization = "Token $token"
    }
```

---

# 28. REST API Endpoints

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/token/` | Obtain authentication token |

## Articles

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/articles/` | Return approved articles |
| POST | `/api/articles/` | Create an article |
| GET | `/api/articles/<id>/` | Retrieve one article |
| PUT | `/api/articles/<id>/` | Update an article |
| PATCH | `/api/articles/<id>/` | Partially update an article |
| DELETE | `/api/articles/<id>/` | Delete an article |
| GET | `/api/articles/subscribed/` | Reader subscription feed |
| POST | `/api/articles/<id>/approve/` | Approve an article when permitted |

## Newsletters

| Method | Endpoint |
|---|---|
| GET | `/api/newsletters/` |
| POST | `/api/newsletters/` |
| GET | `/api/newsletters/<id>/` |
| PUT | `/api/newsletters/<id>/` |
| PATCH | `/api/newsletters/<id>/` |
| DELETE | `/api/newsletters/<id>/` |

## Publishers

```text
GET /api/publishers/
GET /api/publishers/<id>/
```

## Users

```text
GET /api/users/
GET /api/users/<id>/
```

## Internal Approved Article Endpoint

```text
POST /api/approved/
```

---

# 29. Main Frontend Routes

| Route | Purpose |
|---|---|
| `/` | Home / approved articles |
| `/register/` | User registration |
| `/accounts/login/` | Login |
| `/subscriptions/` | Reader subscriptions |
| `/journalist/articles/` | Journalist article management |
| `/articles/create/` | Create article |
| `/newsletters/` | Newsletter list |
| `/newsletters/create/` | Create newsletter |
| `/editor/review/` | Editor article review |
| `/publisher/` | Publisher profile |
| `/publisher/employees/` | Publisher employee management |
| `/admin/` | Django maintenance administration |

---

# 30. Automated Tests

Run:

```powershell
python manage.py test
```

Tests should cover:

- unauthenticated access
- Reader permissions
- Reader subscription filtering
- Journalist article creation
- Journalist edit/delete restrictions
- Journalist approval restrictions
- Editor approval
- Publisher membership
- newsletter behaviour
- signal email logic
- internal API logic
- successful API requests
- failed API requests

A successful test run ends with:

```text
OK
```

---

# 31. Troubleshooting

## `Unknown command: create_default_admin`

The directory must be:

```text
news/
└── management/
    ├── __init__.py
    └── commands/
        ├── __init__.py
        └── create_default_admin.py
```

The folder name is `commands`, not `command`.

Check with:

```powershell
python manage.py help create_default_admin
```

## Publisher Employees page returns 404

A Publisher user must have a linked Publisher profile.

New Publisher registrations create this profile automatically.

Older Publisher test users may not have one. The Publisher views use `get_or_create()` so an older Publisher profile can be created automatically when the Publisher opens the Publisher area.

## Login redirects to `/accounts/profile/`

Make sure `settings.py` contains:

```python
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
```

## Login template missing

Make sure this file exists:

```text
news/templates/registration/login.html
```

## CSS not loading

Make sure:

```text
news/static/news/style.css
```

exists and `base.html` contains:

```django
{% load static %}
```

## MySQL connection fails

Check that:

1. MySQL Server is running.
2. The database is named `enewsapp`.
3. The username is correct.
4. The password is correct.
5. Port `3306` is available.

---

# 32. Project Structure

```text
eNewsApp/
│
├── manage.py
├── README.md
├── requirements.txt
│
├── eNewsApp/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
└── news/
    ├── admin.py
    ├── api_urls.py
    ├── api_views.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── permissions.py
    ├── serializers.py
    ├── signals.py
    ├── tests.py
    ├── urls.py
    ├── views.py
    ├── management/
    │   ├── __init__.py
    │   └── commands/
    │       ├── __init__.py
    │       └── create_default_admin.py
    ├── static/
    │   └── news/
    │       └── style.css
    └── templates/
        ├── news/
        │   ├── base.html
        │   ├── home.html
        │   ├── register.html
        │   ├── editor_review.html
        │   ├── journalist_articles.html
        │   ├── article_form.html
        │   ├── article_confirm_delete.html
        │   ├── newsletter_list.html
        │   ├── newsletter_form.html
        │   ├── newsletter_confirm_delete.html
        │   ├── subscriptions.html
        │   ├── publisher_dashboard.html
        │   └── publisher_employees.html
        └── registration/
            └── login.html
```

---

# 33. GitHub Workflow

Check changed files:

```powershell
git status
```

Add files:

```powershell
git add .
```

Commit:

```powershell
git commit -m "Complete eNews application"
```

Push:

```powershell
git push
```

Make sure these are ignored:

```text
.venv/
__pycache__/
*.pyc
```

---

# 34. Security Notes

This project is intended for development and assessment.

Before production:

1. Change the temporary Administrator password.
2. Remove or disable hard-coded assessment credentials.
3. Set `DEBUG = False`.
4. Configure `ALLOWED_HOSTS`.
5. Store `SECRET_KEY` securely.
6. Store database credentials outside source code.
7. Store internal API keys outside source code.
8. Use HTTPS.
9. Configure a production email service.
10. Review all API permissions.
11. Verify Publisher employee ownership checks.
12. Verify Editor-to-Publisher approval checks.

---

# 35. Quick Start

For a completely new user:

```powershell
git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
cd YOUR-REPOSITORY

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Create the database:

```powershell
mysql -u root -p
```

```sql
CREATE DATABASE enewsapp
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

EXIT;
```

Configure the local MySQL password in `eNewsApp/settings.py`.

Then run:

```powershell
python manage.py migrate
python manage.py create_default_admin
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Temporary Administrator credentials:

```text
Username: examiner_admin
Password: ChangeMeNow!2026
```

> **Change the temporary Administrator password immediately after first login.**

---

# 36. Publisher Role Summary

The Publisher role is the key control that prevents Editors from giving themselves approval privileges.

A Publisher:

1. registers through the normal application
2. receives a Publisher profile
3. acts as the employer
4. adds registered Journalists and Editors
5. controls who may create or approve content for that Publisher

An Editor who only registers as an Editor does **not** automatically gain Publisher approval rights.

A Journalist who only registers as a Journalist does **not** automatically gain access to every Publisher.

Publisher membership is therefore separate from the user's basic role.

```text
User registers
        ↓
Publisher controls employment
        ↓
Employment controls Publisher access
        ↓
Editor / Journalist performs authorised work
```

This separates registration from Publisher-specific privileges and prevents users from assigning themselves access to another Publisher's content.
