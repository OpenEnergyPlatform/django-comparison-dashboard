# Django Comparison Dashboard

This app holds functionality to examine and compare scenario data from various sources (OEP, databus, CSVs).

## Installation

Install app via pip (currently only as GitHub dependency):

```bash
pip install git+https://github.com/OpenEnergyPlatform/django-comparison-dashboard
```

Add app to your installed apps in django project settings:
```python
DJANGO_APPS = [
    ...,
    "django-comparison-dashboard",
]
```

## Requirements

Make sure `django-template-partials` is set up in project.
See https://github.com/carltongibson/django-template-partials#installation for instructions.

Make sure `X-CRSFToken` is set for secure HTMX request.
This can be done by setting body attribute `hx-headers` like this:
```html
<body hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}'>
```
