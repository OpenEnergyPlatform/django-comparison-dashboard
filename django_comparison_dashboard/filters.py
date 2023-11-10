import django_filters

from .models import ScalarData


class FormFilter(django_filters.FilterSet):
    region = django_filters.ModelMultipleChoiceFilter(field_name="region", queryset=ScalarData.objects.all())
    input_energy_vector = django_filters.ModelMultipleChoiceFilter(
        field_name="input_energy_vector", queryset=ScalarData.objects.all()
    )
    output_energy_vector = django_filters.ModelMultipleChoiceFilter(
        field_name="output_energy_vector", queryset=ScalarData.objects.all()
    )
    parameter_name = django_filters.ModelMultipleChoiceFilter(
        field_name="parameter_name", queryset=ScalarData.objects.all()
    )
    technology = django_filters.ModelMultipleChoiceFilter(field_name="technology", queryset=ScalarData.objects.all())
    technology_type = django_filters.ModelMultipleChoiceFilter(
        field_name="technology_type", queryset=ScalarData.objects.all()
    )

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
