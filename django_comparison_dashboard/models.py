from django.contrib.postgres.fields import ArrayField
from django.db import models


class Source(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)


class Scenario(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="scenarios")


class Data(models.Model):
    id = models.BigAutoField(primary_key=True)
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

    class Meta:
        abstract = True


class ScalarData(Data):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="scalars")
    value = models.FloatField()
    year = models.IntegerField()

    filters = (
        "region",
        "year",
        "input_energy_vector",
        "output_energy_vector",
        "parameter_name",
        "technology",
        "technology_type",
    )


class TimeseriesData(Data):
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, related_name="timeseries")
    timeindex_start = models.TimeField()
    timeindex_stop = models.TimeField()
    timeindex_resolution = models.DurationField()
    series = ArrayField(models.FloatField())
