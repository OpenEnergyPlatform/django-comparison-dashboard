import abc
import logging

import pandas as pd
import pandera
import pandera.io
from django.shortcuts import get_object_or_404

from django_comparison_dashboard import forms, models, settings


class SourceRegistry:
    _instance = None
    sources = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, source: type["DataSource"]):
        cls.sources[source.name] = source

    def __getitem__(self, item):
        if item in self.sources:
            return self.sources[item]
        raise KeyError(
            f"Can not find source '{item}' in source registry. Maybe you forgot to register it in the first place?"
        )


class ScenarioValidationError(Exception):
    """Raised if scenario is not valid"""


class Scenario(abc.ABC):
    source_name: str = None

    def __init__(self, scenario_id, data_type: settings.DataType | str):
        if self.source_name is None:
            raise RuntimeError("Source name not defined.")
        self.id = scenario_id
        self.data_type = data_type if isinstance(data_type, settings.DataType) else settings.DataType[data_type]

    def __str__(self):
        """Return string representation of scenario"""
        return self.id

    @property
    def source(self):
        return SourceRegistry()[self.source_name]

    def is_present(self) -> bool:
        return models.Result.objects.filter(name=self.id, source__name=self.source.name).exists()

    def get(self) -> models.Result:
        return get_object_or_404(models.Result.objects.filter(name=self.id, source__name=self.source.name))

    def download(self):
        """Download scenario data, validate data and store in DB if data is valid"""
        data = self.source.download_scenario(self)
        self._validate(data)
        self._store_in_db(data)
        logging.info(f"Successfully downloaded scenario '{self}'.")

    def _store_in_db(self, data: pd.DataFrame):
        """
        Store data into corresponding database model (scalar or timeseries)

        Parameters
        ----------
        data: dict | pd.DataFrame
            Iterable data which shall be stored in DB
        """
        source = models.Source.objects.get_or_create(name=self.source.name)[0]
        scenario = models.Result.objects.get_or_create(name=self.id, source=source)[0]
        if self.data_type == settings.DataType.Scalar:
            data_model = models.ScalarData
        elif self.data_type == models.TimeseriesData:
            data_model = models.TimeseriesData
        else:
            raise TypeError(f"Unknown data type '{self.data_type}'.")
        data_model.objects.bulk_create(
            data_model(scenario=scenario, **item) for item in data.to_dict(orient="records")
        )

    def _validate(self, data: pd.DataFrame) -> None:
        """
        Validate given data using pandera and source-related schema

        Parameters
        ----------
        data: pandas.DataFrame
            Data to validate

        Returns
        -------
        dict
            in case of an error a report is returned, otherwise None is returned

        Raises
        ------
        pandera.errors.SchemaError
            if scenario data does not fit into OEDatamodel format
        """
        logging.info(f"Validating data for scenario {self}...")
        schema = pandera.io.from_frictionless_schema(settings.MODEX_OUTPUT_SCHEMA[str(self.data_type)])
        schema.validate(data, lazy=True)


class DataSource(abc.ABC):
    name: str = None
    scenario: type[Scenario] = None
    form = forms.DataSourceUploadForm

    @classmethod
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
