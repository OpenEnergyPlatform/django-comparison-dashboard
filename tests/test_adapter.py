import pathlib

import pandas as pd
import pandera
from django.test import TestCase

from django_comparison_dashboard import settings
from django_comparison_dashboard.adapters.core import DataAdapter
from django_comparison_dashboard.sources.csv import CSVDataSource, CSVScenario


class TestAdapter(DataAdapter):
    name = "Test"

    @classmethod
    def transform(cls, data: pd.DataFrame):
        # Add column "technology_type":
        data["technology_type"] = data["technology"]
        # Transform region color into list:
        data["region"] = data["region"].apply(lambda x: [x])
        # Reorder columns
        order = [field["name"] for field in settings.MODEX_OUTPUT_SCHEMA["oed_scalars"]["fields"]]
        data = data.reindex(order, axis=1)
        return data


class AdapterTest(TestCase):
    def test_adapter(self):
        csv_filepath = pathlib.Path(__file__).parent / "_files" / "oed_scalar_transformed.csv"
        with csv_filepath.open("r", encoding="utf-8") as csv_file:
            scenario = CSVScenario(1, settings.DataType.Scalar, csv_file)
            data_raw = CSVDataSource.download_scenario(scenario)
            with self.assertRaises(pandera.errors.SchemaErrors):
                scenario._validate(data_raw)
            data_transformed = TestAdapter.transform(data_raw)
            scenario._validate(data_transformed)
