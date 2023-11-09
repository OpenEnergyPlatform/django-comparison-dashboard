import json
import logging

import requests

from django_comparison_dashboard import settings
from django_comparison_dashboard.sources import core

OEP_URL = "https://openenergyplatform.org"
CONNECTOR_URL = "https://modex.rl-institut.de/scenario/id/"


class ModexScenario(core.Scenario):
    source_name = "MODEX"

    def __init__(self, scenario_id: int, data_type: settings.DataType):
        super().__init__(scenario_id, data_type)


class ModexDataSource(core.DataSource):
    name = "MODEX"
    scenario = ModexScenario

    @classmethod
    def list_scenarios(cls) -> list[core.Scenario]:
        fields = ["scenario", "id", "source"]
        query = {
            "fields": fields,
            "distinct": True,
            "from": {
                "type": "table",
                "table": "oed_scenario_output",
                "schema": "model_draft",
            },
            "order_by": [{"type": "column", "column": "id"}],
        }
        response = requests.post(OEP_URL + "/api/v0/advanced/search", json={"query": query}, allow_redirects=False)
        data = response.json()["data"]
        scenario_fields = ("name", "scenario_id", "framework")
        scenarios = [dict(zip(scenario_fields, row)) for row in data]
        return [
            ModexScenario(**scenario, data_type=data_type) for scenario in scenarios for data_type in settings.DataType
        ]

    @classmethod
    def download_scenario(cls, scenario: ModexScenario) -> list[dict]:
        """
        Download scenario data from OEDatamodel_API using table name and scenario ID

        Returns
        -------
        pd.DataFrame
            holding scenario data
        """
        logging.info(f"Requesting data for scenario '{scenario}' (Source: {cls.name})...")
        table = str(scenario.data_type)
        response = requests.get(
            CONNECTOR_URL + str(scenario.id),
            {
                "mapping": json.dumps(
                    {
                        "base_mapping": "concrete",
                        "mapping": {
                            table: f"map(&set(@, 'region', join(',', @.region)), {table})",
                        },
                    }
                ),
                "source": "modex_output",
            },
            timeout=10000,
            verify=False,
        )
        logging.info(f"Loading data for scenario {scenario}...")
        data = json.loads(response.text)
        return [{k: v for k, v in d.items() if k not in ("id", "scenario_id")} for d in data[table]]
