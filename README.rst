
.. figure:: https://user-images.githubusercontent.com/14353512/185425447-85dbcde9-f3a2-4f06-a2db-0dee43af2f5f.png
    :align: left
    :target: https://github.com/rl-institut/super-repo/
    :alt: Repo logo

===========================
Django Comparison Dashboard
===========================

.. list-table::
   :widths: auto

   * - License
     - |badge_license|
   * - Documentation
     - |badge_documentation|
   * - Publication
     -
   * - Development
     - |badge_issue_open| |badge_issue_closes| |badge_pr_open| |badge_pr_closes|
   * - Community
     - |badge_contributing| |badge_contributors| |badge_repo_counts|

This app holds functionality to examine and compare scenario data from various sources (OEP, databus, CSVs).

.. contents::
    :depth: 2
    :local:
    :backlinks: top

Requirements
============

Make sure `django-template-partials` is set up in project.
See https://github.com/carltongibson/django-template-partials#installation for instructions.

Make sure `X-CRSFToken` is set for secure HTMX request.
This can be done by setting body attribute `hx-headers` like this:

.. code-block:: html

    <body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>


Installation
============
Install app via pip (currently only as GitHub dependency):

.. code-block:: bash

    pip install git+https://github.com/OpenEnergyPlatform/django-comparison-dashboard

Add app to your installed apps in django project settings:

.. code-block:: python

    DJANGO_APPS = [
        ...,
        "django-comparison-dashboard",
    ]

For Developers
============

You can download example scenario from MODEX like this:

.. code-block:: bash

    export DJANGO_READ_DOT_ENV_FILE=True; python manage.py shell

within the shell run

.. code-block:: python

    from django_comparison_dashboard.sources import modex

    modex.ModexDataSource.list_scenarios()[-2].download()

to download example data.


.. |badge_license| image:: https://img.shields.io/github/license/OpenEnergyPlatform/django-comparison-dashboard.svg
    :target: LICENSE.txt
    :alt: License

.. |badge_documentation| image::
    :target:
    :alt: Documentation

.. |badge_contributing| image:: https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat
    :alt: contributions

.. |badge_repo_counts| image:: http://hits.dwyl.com/OpenEnergyPlatform/django-comparison-dashboard.svg
    :alt: counter

.. |badge_contributors| image:: https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square
    :alt: contributors

.. |badge_issue_open| image:: https://img.shields.io/github/issues-raw/OpenEnergyPlatform/django-comparison-dashboard
    :alt: open issues

.. |badge_issue_closes| image:: https://img.shields.io/github/issues-closed-raw/OpenEnergyPlatform/django-comparison-dashboard
    :alt: closes issues

.. |badge_pr_open| image:: https://img.shields.io/github/issues-pr-raw/OpenEnergyPlatform/django-comparison-dashboard
    :alt: closes issues

.. |badge_pr_closes| image:: https://img.shields.io/github/issues-pr-closed-raw/OpenEnergyPlatform/django-comparison-dashboard
    :alt: closes issues
