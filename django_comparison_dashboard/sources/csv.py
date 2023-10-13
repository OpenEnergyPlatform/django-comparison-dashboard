from django_comparison_dashboard import forms, settings
from django_comparison_dashboard.sources import core


class CSVScenario(core.Scenario):
    def __init__(self, scenario_id: int, data_type: settings.DataType, file):
        super().__init__(scenario_id, data_type)
        self.file = file

    def __str__(self):
        return f"{self.id} ({self.file.name})"


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
        print(scenario.file)
