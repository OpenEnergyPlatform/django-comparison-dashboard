import abc

import pandas


class DataSource(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def list_scenarios(cls) -> list[str]:
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
    def download_scenario_data(cls, identifier: str) -> None:
        """
        Download data and store it in DB

        Parameters
        ----------
        identifier: str
            Name or URL of scenario from which data can be downloaded
        """
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def validate_scenario_data(data: dict[str, pandas.DataFrame]) -> dict | None:
        """
        Validate given data using frictionless and source-related schema

        Parameters
        ----------
        data: dict[str, pandas.DataFrame]
            Data to validate

        Returns
        -------
        dict
            in case of an error a frictionless error report is returned, otherwise None is returned
        """
        raise NotImplementedError
