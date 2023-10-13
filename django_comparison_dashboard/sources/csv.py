import csv
from io import TextIOWrapper

from django_comparison_dashboard import forms, settings
from django_comparison_dashboard.sources import core


class CSVScenario(core.Scenario):
    source_name = "CSV"

    def __init__(self, scenario_id: int, data_type: settings.DataType, csv_file):
        super().__init__(scenario_id, data_type)
        self.csv_file = csv_file

    def __str__(self):
        return f"{self.id} ({self.csv_file.name})"


class CSVDataSource(core.DataSource):
    name = "CSV"
    scenario = CSVScenario
    form = forms.CSVSourceUploadForm

    @classmethod
    def download_scenario(cls, scenario: CSVScenario) -> list[dict]:
        """
        Download scenario data from CSV file

        Returns
        -------
        pd.DataFrame
            holding scenario data
        """
        csv_text = TextIOWrapper(scenario.csv_file, encoding="utf-8")
        csv_reader = csv.DictReader(csv_text, delimiter=";")
        return [row for row in csv_reader]
