import django_filters

from .models import ScalarData


class FormFilter(django_filters.FilterSet):
    def __init__(self, scenarios, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        for field in ScalarData.filters:
            qs = ScalarData.objects.filter(scenario__in=scenarios).order_by().values_list(field, flat=True).distinct()
            field_instance = django_filters.MultipleChoiceFilter(
                field_name=field, choices=[(choice, choice) for choice in qs.all()]
            )
            self.filters[field] = field_instance

    class Meta:
        model = ScalarData
        fields = [
            "region",
            "input_energy_vector",
            "output_energy_vector",
            "parameter_name",
            "technology",
            "technology_type",
        ]
