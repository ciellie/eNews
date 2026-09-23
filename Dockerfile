# Use a lightweight Python 3.14 image as the base image.
FROM python:3.14-slim


# Prevent Python from creating .pyc files inside the container.
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure Python output is sent directly to the terminal/logs
# without being buffered.
ENV PYTHONUNBUFFERED=1


# Set the working directory inside the container.
# All following commands will run from /app.
WORKDIR /app


# Install the Linux packages required to build and use
# the mysqlclient Python package.
#
# build-essential:
#   Provides compilers and build tools needed by Python packages.
#
# default-libmysqlclient-dev:
#   Provides the MySQL client development libraries.
#
# pkg-config:
#   Helps the build process locate installed libraries.
#
# The final command removes cached package information to keep
# the Docker image smaller.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*


# Copy the requirements file into the container first.
# This allows Docker to reuse the dependency-installation layer
# when application code changes but requirements.txt does not.
COPY requirements.txt /app/requirements.txt


# Upgrade pip and install all Python dependencies required
# by the Django application.
#
# --no-cache-dir prevents pip from keeping package-download caches
# and helps reduce the final Docker image size.
RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r /app/requirements.txt


# Copy the complete Django project into the container.
COPY . /app


# Document that the application listens on port 8000.
EXPOSE 8000


# Start the Django application using Gunicorn.
#
# eNewsApp.wsgi:application:
#   Loads the Django WSGI application.
#
# --bind 0.0.0.0:8000:
#   Makes the application accessible outside the container.
#
# --workers 3:
#   Starts three Gunicorn worker processes.
#
# --timeout 120:
#   Allows a worker up to 120 seconds to complete a request
#   before Gunicorn terminates it.
CMD [
    "gunicorn",
    "eNewsApp.wsgi:application",
    "--bind",
    "0.0.0.0:8000",
    "--workers",
    "3",
    "--timeout",
    "120"
]
