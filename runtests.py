#!/usr/bin/env python

import sys

import django
import environ
from django.conf import settings
from django.core.management import call_command

env = environ.Env()


def runtests():
    if not settings.configured:
        # Choose database for settings
        DATABASES = {"default": env.db("DATABASE_URL")}

        # Configure test environment
        settings.configure(
            DATABASES=DATABASES,
            INSTALLED_APPS=(
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django.contrib.sites",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "django_comparison_dashboard",
            ),
            ROOT_URLCONF="",  # tests override urlconf, but it still needs to be defined
            MIDDLEWARE_CLASSES=(
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
            ),
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
        )

    django.setup()
    failures = call_command(
        "test",
        "django_comparison_dashboard",
        interactive=False,
        failfast=False,
        verbosity=2,
    )

    sys.exit(bool(failures))


if __name__ == "__main__":
    runtests()
