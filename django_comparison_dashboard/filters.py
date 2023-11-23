import django_filters

from .models import ScalarData


class FormFilter(django_filters.FilterSet):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        for field in ScalarData.filters:
            qs = self.queryset.order_by().values_list(field, flat=True).distinct()
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


def available_filters():
    # get available filters from FormFilter
    available_filters = [(count, filter_name) for count, filter_name in enumerate(ScalarData.filters)]
    # needs to be filtered by chosen scenarios
    return available_filters


class GraphOptionFilter(django_filters.FilterSet):
    x = django_filters.ChoiceFilter(label="X-Axis", choices=available_filters)
    y = django_filters.ChoiceFilter(label="Y-Axis", choices=available_filters)
    text = django_filters.ChoiceFilter(label="Text", choices=available_filters)
    color = django_filters.ChoiceFilter(label="Color", choices=available_filters)
    hover_name = django_filters.ChoiceFilter(label="Hover", choices=available_filters)
    orientation = django_filters.ChoiceFilter(label="Orientation", choices=((0, "vertical"), (1, "horizontal")))
    barmode = django_filters.ChoiceFilter(label="Mode", choices=((0, "relative"), (1, "group"), (2, "overlay")))
    facet_col = django_filters.ChoiceFilter(label="Subplots", choices=available_filters)
    facet_col_wrap = django_filters.NumberFilter(label="Subplots per Row")

    class Meta:
        fields = [
            "x_axis",
            "y-axis",
            "text",
            "color",
            "hover",
            "barmode",
            "facet_col",
            "facet_col_wrap",
        ]
