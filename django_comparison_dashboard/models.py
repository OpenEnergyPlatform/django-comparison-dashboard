from django.contrib.postgres.fields import ArrayField
from django.db import models


class Source(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Result(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="results")


class ScalarData(models.Model):
    id = models.BigAutoField(primary_key=True)
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name="scalars")

    scenario = models.CharField(max_length=255)
    process = models.CharField(max_length=255)
    parameter = models.CharField(max_length=255)
    value = models.FloatField()
    year = models.IntegerField()
    input_commodity = models.CharField(max_length=255, null=True)
    output_commodity = models.CharField(max_length=255, null=True)
    sector = models.CharField(max_length=255)
    category = models.CharField(max_length=255, null=True)
    specification = models.CharField(max_length=255, null=True)
    new = models.BooleanField()
    unit = models.CharField(max_length=255)
    groups = ArrayField(models.CharField(max_length=255), null=True)

    filters = [
        "scenario",
        "process",
        "parameter",
        "groups",
        "input_commodity",
        "output_commodity",
        "sector",
        "category",
        "specification",
        "new",
        "year",
    ]


class FilterSettings(models.Model):
    name = models.CharField(max_length=255, unique=True)
    filter_set = models.JSONField()
    graph_filter_set = models.JSONField()
