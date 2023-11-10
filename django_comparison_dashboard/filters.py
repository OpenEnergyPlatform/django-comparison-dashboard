import django_filters

from .models import ScalarData


class FormFilter(django_filters.FilterSet):
    """for field in ScalarData.filters:
    field = django_filters.ModelMultipleChoiceFilter(
        field_name=field, queryset=ScalarData.objects.order_by().values_list(field flat=True).distinct()
        )
    """

    scenario = django_filters.ModelMultipleChoiceFilter(
        field_name="scenario", queryset=ScalarData.objects.order_by().values_list("scenario", flat=True).distinct()
    )
    region = django_filters.ModelMultipleChoiceFilter(
        field_name="region", queryset=ScalarData.objects.order_by().values_list("region", flat=True).distinct()
    )
    input_energy_vector = django_filters.ModelMultipleChoiceFilter(
        field_name="input_energy_vector",
        queryset=ScalarData.objects.order_by().values_list("input_energy_vector", flat=True).distinct(),
    )
    output_energy_vector = django_filters.ModelMultipleChoiceFilter(
        field_name="output_energy_vector",
        queryset=ScalarData.objects.order_by().values_list("output_energy_vector", flat=True).distinct(),
    )
    parameter_name = django_filters.ModelMultipleChoiceFilter(
        field_name="parameter_name",
        queryset=ScalarData.objects.order_by().values_list("parameter_name", flat=True).distinct(),
    )
    technology = django_filters.ModelMultipleChoiceFilter(
        field_name="technology", queryset=ScalarData.objects.order_by().values_list("technology", flat=True).distinct()
    )
    technology_type = django_filters.ModelMultipleChoiceFilter(
        field_name="technology_type",
        queryset=ScalarData.objects.order_by().values_list("technology_type", flat=True).distinct(),
    )

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)
        if request is not None:
            scenario_values = request.GET.getlist("scenario_ids")
            if scenario_values:
                self.filters["scenario"].extra["initial"] = scenario_values

    class Meta:
        model = ScalarData
        fields = [
            "scenario",
            "region",
            "input_energy_vector",
            "output_energy_vector",
            "parameter_name",
            "technology",
            "technology_type",
        ]
