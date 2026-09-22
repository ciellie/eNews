# eNewsApp

eNewsApp is a Django-based news application with role-based access for **Readers, Journalists, Editors, and Publishers**.

The application includes:

- user registration and login
- Publisher profiles and employee management
- independent Journalist and Publisher articles
- article review and approval
- newsletters
- Reader subscriptions
- Django REST Framework API endpoints
- token authentication
- email notifications and Django signals
- MySQL
- automated tests
- Sphinx documentation
- Docker support

---

# 1. Application Roles

| Role | Main purpose |
|---|---|
| Reader | Reads approved content and subscribes to Publishers and Journalists |
| Journalist | Creates articles and newsletters |
| Editor | Reviews and approves content when assigned to a Publisher |
| Publisher | Acts as an employer and manages its Journalists and Editors |

The **Publisher** role controls which Journalists and Editors may act on behalf of a Publisher.

A Journalist cannot create content for an unrelated Publisher, and an Editor cannot approve Publisher content merely because they registered as an Editor.

---

# 2. Security and Secrets

**Do not commit passwords, access tokens, Django secret keys, API keys, or other credentials to GitHub.**

This project should receive secrets from environment variables or from a local `.env` file that is excluded from Git.

The following values must be supplied locally:

- MySQL database password
- Django `SECRET_KEY`
- internal API key
- Docker MySQL passwords
- reviewer/admin passwords
- any REST API tokens used during testing

## Generate a Django secret key

After installing the Python dependencies, run:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and use it as `DJANGO_SECRET_KEY`.

## Generate an internal API key

Run:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as `INTERNAL_API_KEY`.

## Reviewer credentials

Do **not** put reviewer usernames or passwords in this public README.

For assessment, create a local file named:

```text
REVIEWER_CREDENTIALS.txt
```

Add it to `.gitignore` so it is never pushed to GitHub.

A template is supplied as:

```text
REVIEWER_CREDENTIALS_TEMPLATE.txt
```

Copy the template, enter the temporary credentials, and include the completed `REVIEWER_CREDENTIALS.txt` only in the private assessment submission if the reviewer requires quick access.

After the task has been marked, remove that temporary credentials file.

---

# 3. Clone the Project

A new user must first obtain the project from GitHub.

```powershell
git clone https://github.com/ciellie/eNews.git
```

Enter the cloned folder:

```powershell
cd eNews
```

Confirm that the project files are present:

```powershell
dir
```

You should see files such as:

```text
manage.py
requirements.txt
README.md
Dockerfile
docker-compose.yml
```

All following commands should be run from this project directory unless stated otherwise.

---

# 4. Build and Run with a Python Virtual Environment

This section explains how to run the project directly with Python and a local MySQL installation.

## 4.1 Requirements

Install:

1. Python 3
2. MySQL Server
3. Git
4. pip

Check Python:

```powershell
python --version
```

Check pip:

```powershell
pip --version
```

Check MySQL:

```powershell
mysql --version
```

If the `mysql` command is not available on Windows, use **MySQL Command Line Client**.

## 4.2 Create the virtual environment

Create the virtual environment **inside the cloned project folder**:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

## 4.3 Install the project dependencies

Run from the directory containing `requirements.txt`:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4.4 Create the local MySQL database

Open MySQL:

```powershell
mysql -u root -p
```

The password entered here is the password configured for the local MySQL installation. It is not supplied by the project.

Create the database:

```sql
CREATE DATABASE enewsapp
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

Confirm it exists:

```sql
SHOW DATABASES;
```

Exit:

```sql
EXIT;
```

## 4.5 Set the required environment variables

For a PowerShell session:

```powershell
$env:DB_NAME="enewsapp"
$env:DB_USER="root"
$env:DB_PASSWORD="YOUR_LOCAL_MYSQL_PASSWORD"
$env:DB_HOST="localhost"
$env:DB_PORT="3306"

$env:DJANGO_SECRET_KEY="YOUR_GENERATED_DJANGO_SECRET_KEY"
$env:DJANGO_DEBUG="True"
$env:DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

$env:INTERNAL_API_KEY="YOUR_GENERATED_INTERNAL_API_KEY"
$env:APPROVED_ARTICLE_API_URL="http://127.0.0.1:8000/api/approved/"
```

Replace the placeholder values with secrets generated or chosen locally.

Do not add these real values to GitHub.

## 4.6 Apply migrations

The project migrations are included in the repository.

```powershell
python manage.py migrate
```

Use `makemigrations` only after changing Django models during development.

## 4.7 Create a local maintenance administrator

Use Django's normal command:

```powershell
python manage.py createsuperuser
```

Choose the username, email address, and password locally.

Do not place the password in the README or source code.

Django Admin is for maintenance only and is not used as the normal application workflow for assigning Publisher employees.

## 4.8 Run the development server

```powershell
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

Login:

```text
http://127.0.0.1:8000/accounts/login/
```

Registration:

```text
http://127.0.0.1:8000/register/
```

Maintenance Admin:

```text
http://127.0.0.1:8000/admin/
```

Stop the server with:

```text
Ctrl+C
```

## 4.9 Run the tests with the virtual environment

```powershell
python manage.py check
python manage.py test
```

A successful test run ends with:

```text
OK
```

---

# 5. Build and Run with Docker

Docker is the easiest way to run the application on another computer because the Docker configuration supplies both the Django application and MySQL.

The other computer does **not** need its own Python virtual environment or local MySQL installation.

## 5.1 Requirements

Install:

- Git
- Docker Desktop, or another environment with Docker Engine and Docker Compose

Check Docker:

```powershell
docker --version
docker compose version
```

## 5.2 Clone the project

```powershell
git clone https://github.com/ciellie/eNews.git
cd eNews
```

## 5.3 Create the Docker environment file

The repository should contain:

```text
.env.example
```

Copy it to a local `.env` file:

```powershell
Copy-Item .env.example .env
```

On Linux/macOS:

```bash
cp .env.example .env
```

Open `.env` and replace the example values with locally chosen secrets.

Example structure:

```text
MYSQL_DATABASE=enewsapp
MYSQL_USER=enewsuser
MYSQL_PASSWORD=CHOOSE_A_STRONG_DATABASE_PASSWORD
MYSQL_ROOT_PASSWORD=CHOOSE_A_DIFFERENT_ROOT_PASSWORD

DJANGO_SECRET_KEY=PASTE_A_GENERATED_DJANGO_SECRET_KEY
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

INTERNAL_API_KEY=PASTE_A_GENERATED_INTERNAL_API_KEY
APPROVED_ARTICLE_API_URL=http://127.0.0.1:8000/api/approved/
```

The `.env` file must be listed in `.gitignore`.

Do not commit it.

For a remote Docker playground, set `DJANGO_ALLOWED_HOSTS` to the hostname supplied by the playground.

## 5.4 Build and start the containers

```powershell
docker compose up --build
```

On first startup Docker will:

1. build the Django image
2. download/start MySQL
3. wait for MySQL to become healthy
4. run Django migrations
5. collect static files
6. start Gunicorn on port 8000

A successful startup includes output similar to:

```text
Applying migrations... OK
static files copied
Starting gunicorn
Listening at: http://0.0.0.0:8000
```

The terminal remains attached to the running containers. This is normal.

Open:

```text
http://localhost:8000/
```

## 5.5 Run Docker in the background

Alternatively:

```powershell
docker compose up --build -d
```

View the running containers:

```powershell
docker compose ps
```

View logs:

```powershell
docker compose logs -f web
```

## 5.6 Create a maintenance administrator in Docker

With the containers running:

```powershell
docker compose exec web python manage.py createsuperuser
```

Choose the credentials locally.

If credentials are required by the assessor, record the temporary values in the private `REVIEWER_CREDENTIALS.txt` file, not in GitHub.

## 5.7 Run checks and tests inside Docker

```powershell
docker compose exec web python manage.py check
docker compose exec web python manage.py test
```

## 5.8 Stop Docker

If Docker is running in the foreground, press:

```text
Ctrl+C
```

Then:

```powershell
docker compose down
```

To delete the MySQL Docker volume and start with a completely empty database:

```powershell
docker compose down -v
```

> `-v` permanently deletes the Docker database volume.

---

# 6. Docker Files

The repository includes:

```text
Dockerfile
docker-compose.yml
.dockerignore
.env.example
```

The Docker setup runs:

```text
Django + Gunicorn
        |
        v
      MySQL
```

The web container exposes port `8000` and connects to MySQL using the Docker service hostname `db`.

The database credentials are supplied through environment variables rather than being committed to the repository.

---

# 7. User Registration

Users register through:

```text
/register/
```

Supported roles are:

- Reader
- Journalist
- Editor
- Publisher

Editors may register normally, but registration alone does not give them approval access to a Publisher.

---

# 8. Publisher Role

The **Publisher** role acts like an employer.

A Publisher account has a Publisher profile and manages its employees through the normal application frontend.

A Publisher can add registered users as:

- Journalists
- Editors

A Publisher can also remove those employees later.

The Publisher does not create passwords for its employees. Journalists and Editors register their own accounts.

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
That user may act for the Publisher
```

## Publisher responsibilities

A Publisher can:

- view its Publisher profile
- view its employee list
- add registered Journalists
- add registered Editors
- remove Journalists
- remove Editors

A Publisher may only manage its own Publisher profile and employees.

## Publisher routes

Publisher profile:

```text
/publisher/
```

Employee management:

```text
/publisher/employees/
```

---

# 9. Journalist Role

A Journalist can:

- create independent articles
- edit their own independent articles
- delete their own independent articles
- create newsletters
- edit their own newsletters
- delete their own newsletters

A Journalist may create an article for a Publisher only when that Publisher has added the Journalist as an employee.

A Journalist cannot approve an article.

---

# 10. Editor Role

An Editor can register through the normal registration process.

A newly registered Editor does not automatically gain Publisher approval privileges.

The workflow is:

```text
Editor registers
        ↓
Publisher adds Editor
        ↓
Editor becomes active for that Publisher
```

For a Publisher article:

- the Editor must belong to that Publisher
- the Editor may then review and approve the Publisher's article

For an independent Journalist article, an active Editor may review and approve it according to the application's permission rules.

---

# 11. Reader Role

A Reader can:

- log in
- view newsletters
- subscribe to Publishers
- subscribe to Journalists
- view approved articles from those subscriptions
- use the subscribed-content REST API endpoint

Readers do not subscribe directly to newsletters.

A logged-in Reader sees approved articles from subscribed Publishers and Journalists.

---

# 12. Public Visitors

A visitor who is not logged in can:

- view all approved articles
- register
- log in

---

# 13. Article Rules

An Article contains:

- `title`
- `content`
- `author`
- `created_at`
- `approved`
- `publisher`

An article belongs to either:

- an independent Journalist, or
- a Publisher

It must not belong to both simultaneously.

New articles are created with:

```text
approved = False
```

## Independent article

```text
author = logged-in Journalist
publisher = None
approved = False
```

## Publisher article

```text
author = None
publisher = selected Publisher
approved = False
```

The Journalist may select only a Publisher that employs them.

---

# 14. Article Approval Workflow

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

A Journalist cannot approve their own article.

For Publisher content, the Editor must belong to the relevant Publisher.

---

# 15. Newsletter Functionality

A Newsletter contains:

- `title`
- `description`
- `created_at`
- `author`
- a many-to-many relationship with Articles

Journalists can create and manage their own newsletters.

Editors can manage newsletters according to the application's permissions.

Readers can view newsletters.

Frontend route:

```text
/newsletters/
```

---

# 16. Reader Subscriptions

Readers subscribe to:

- Publishers
- Journalists

Subscription page:

```text
/subscriptions/
```

The logged-in Reader homepage is filtered to approved articles from those subscriptions.

---

# 17. REST API Authentication

The API uses Django REST Framework Token Authentication.

Obtain a token:

```powershell
$response = Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/token/" `
    -Method POST `
    -Body @{
        username = "YOUR_USERNAME"
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

Do not save real API tokens in source code or commit them to GitHub.

---

# 18. Main Frontend Routes

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
| `/admin/` | Maintenance administration |

---

# 19. Automated Tests

With the virtual environment:

```powershell
python manage.py test
```

With Docker:

```powershell
docker compose exec web python manage.py test
```

---

# 20. Sphinx Documentation

Build the Sphinx documentation:

```powershell
cd docs
.\make.bat html
```

On Linux/macOS:

```bash
cd docs
make html
```

Generated documentation is written to:

```text
docs/_build/html/index.html
```

---

# 21. `.gitignore`

At minimum, the following local/generated files should not be committed:

```text
.venv/
.env
REVIEWER_CREDENTIALS.txt
__pycache__/
*.pyc
*.log
staticfiles/
docs/_build/
```

Before pushing:

```powershell
git status
```

If a secret was accidentally committed, removing it from the current file is not enough. Rotate the exposed credential and clean it from repository history where necessary.

---

# 22. Quick Start Summary

## Virtual environment

```powershell
git clone https://github.com/ciellie/eNews.git
cd eNews

python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Create MySQL database and set local environment variables first.

python manage.py migrate
python manage.py createsuperuser
python manage.py test
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Docker

```powershell
git clone https://github.com/ciellie/eNews.git
cd eNews

Copy-Item .env.example .env

# Edit .env and add locally generated/chosen secrets.

docker compose up --build
```

In another terminal:

```powershell
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py test
```

Open:

```text
http://localhost:8000/
```

---

# 23. Assessment Credential File

If the assessor requires immediate access to prepared accounts, create a local:

```text
REVIEWER_CREDENTIALS.txt
```

Do not commit this file to the public GitHub repository.

It may be included temporarily in a private assessment submission, as requested by the assessor, and removed once the assessment is complete.

The public repository and this README should contain no real passwords, access tokens, or API secrets.
