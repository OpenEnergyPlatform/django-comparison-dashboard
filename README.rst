
.. figure:: https://user-images.githubusercontent.com/14353512/185425447-85dbcde9-f3a2-4f06-a2db-0dee43af2f5f.png
    :align: left
    :target: https://github.com/rl-institut/super-repo/
    :alt: Repo logo

===========================
Django Comparison Dashboard
===========================

This app holds functionality to examine and compare scenario data from various sources (OEP, databus, CSVs).

.. contents::
    :depth: 2
    :local:
    :backlinks: top

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
