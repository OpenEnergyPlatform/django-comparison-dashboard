from django.test import TestCase

from django_comparison_dashboard import models
from django_comparison_dashboard.sources import modex


class ModexSourceTest(TestCase):
    def test_scenario_listing(self):
        scenarios = modex.ModexDataSource.list_scenarios()
        assert isinstance(scenarios, list)
        assert len(scenarios) > 0
        assert isinstance(scenarios[0], modex.ModexScenario)

    def test_download_scenario(self):
        scenarios = modex.ModexDataSource.list_scenarios()
        scenario = scenarios[-2]
        scenario.download()
        assert models.Source.objects.get(name="MODEX")
        assert models.Scenario.objects.get(name=scenario.id, source__name="MODEX")
        assert len(models.ScalarData.objects.all()) > 0
