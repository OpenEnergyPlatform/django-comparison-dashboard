import abc
import logging

import pandas as pd
from django.shortcuts import get_object_or_404
from frictionless import Resource, validate_resource

from django_comparison_dashboard import models, settings


class ScenarioValidationError(Exception):
    """Raised if scenario is not valid"""


class Scenario(abc.ABC):
    source: "DataSource" = None

    def __init__(self, scenario_id, data_type: settings.DataType):
        self.id = scenario_id
        self.data_type = data_type

    @abc.abstractmethod
    def __str__(self):
        """Return string representation of scenario"""

    def is_present(self) -> bool:
        return models.Scenario.objects.filter(name=self.id, source__name=self.source.name).exists()

    def get(self) -> models.Scenario:
        return get_object_or_404(models.Scenario.objects.filter(name=self.id, source__name=self.source.name))

    def download(self):
        """Download scenario data, validate data and store in DB if data is valid"""
        data = self.source.download_scenario(self)
        self._validate(data)
        self._store_in_db(data)
        logging.info(f"Successfully downloaded scenario '{self}'.")

    def _store_in_db(self, data: list[dict] | pd.DataFrame):
        """
        Store data into corresponding database model (scalar or timeseries)

        Parameters
        ----------
        data: dict | pd.DataFrame
            Iterable data which shall be stored in DB
        """
        source = models.Source.objects.get_or_create(name=self.source.name)[0]
        scenario = models.Scenario.objects.get_or_create(name=self.id, source=source)[0]
        data_model = models.ScalarData if self.data_type == settings.DataType.Scalar else models.TimeseriesData
        data_model.objects.bulk_create(data_model(scenario=scenario, **item) for item in data)

    def _validate(self, data: dict | pd.DataFrame) -> None:
        """
        Validate given data using frictionless and source-related schema

        Parameters
        ----------
        data: pandas.DataFrame
            Data to validate

        Returns
        -------
        dict
            in case of an error a frictionless error report is returned, otherwise None is returned

        Raises
        ------
        ScenarioValidationError
            if scenario data does not fit into OEDatamodel format
        """
        logging.info(f"Validating data for scenario {self}...")
        resource = Resource(
            name=str(self.data_type),
            profile="tabular-data-resource",
            data=data,
            schema=settings.MODEX_OUTPUT_SCHEMA[str(self.data_type)],
        )
        report = validate_resource(resource)
        if report["stats"]["errors"] != 0:
            error = ScenarioValidationError(f"Could not validate scenario data for scenario '{self}'.")
            error.add_note(str(report))
            raise error


class DataSource(abc.ABC):
    name: str = None

    @classmethod
    @abc.abstractmethod
    def list_scenarios(cls) -> list[Scenario]:
        """
        List all available scenarios

        Returns
        -------
        list[str]
            List of available scenarios
        """
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def download_scenario(cls, scenario: Scenario) -> pd.DataFrame:
        """
        Download scenario from source

        Parameters
        ----------
        scenario: Scenario
            Download given scenario from source

        Returns
        -------
        pd.DataFrame
            DataFrame containing scenario data
        """
        raise NotImplementedError
