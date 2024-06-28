# Generated by Django 4.2.4 on 2024-06-25 13:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_comparison_dashboard", "0007_rename_filtersettings_namedfiltersettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="FilterSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("filter_set", models.JSONField()),
                ("graph_filter_set", models.JSONField()),
            ],
        ),
    ]