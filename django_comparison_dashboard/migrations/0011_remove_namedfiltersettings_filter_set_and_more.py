# Generated by Django 4.2.4 on 2024-06-25 13:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("django_comparison_dashboard", "0010_namedfiltersettings_filter_settings"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="namedfiltersettings",
            name="filter_set",
        ),
        migrations.RemoveField(
            model_name="namedfiltersettings",
            name="graph_filter_set",
        ),
        migrations.AlterField(
            model_name="namedfiltersettings",
            name="filter_settings",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.DO_NOTHING,
                to="django_comparison_dashboard.filtersettings",
            ),
        ),
    ]
