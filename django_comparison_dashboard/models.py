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
    value = models.FloatField()
    year = models.IntegerField()
    region = models.CharField(max_length=255)
    input_energy_vector = models.CharField(max_length=255, null=True)
    output_energy_vector = models.CharField(max_length=255, null=True)
    parameter_name = models.CharField(max_length=255)
    technology = models.CharField(max_length=255)
    technology_type = models.CharField(max_length=255)
    unit = models.CharField(max_length=255)
    tags = models.JSONField(max_length=255, null=True)
    method = models.JSONField(max_length=255, null=True)
    source = models.CharField(max_length=255, null=True)
    comment = models.CharField(max_length=255, null=True)

    filters = (
        "region",
        "year",
        "input_energy_vector",
        "output_energy_vector",
        "parameter_name",
        "technology",
        "technology_type",
    )


class FilterSettings(models.Model):
    name = models.CharField(max_length=255, unique=True)
    filter_set = models.JSONField()
    graph_filter_set = models.JSONField()
