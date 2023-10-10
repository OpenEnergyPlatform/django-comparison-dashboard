from django import forms


class Scenario(forms.Form):
    scenarios = forms.MultipleChoiceField(
        choices=[
            ("code_exposed_fig1", "code_exposed_fig1"),
            ("base_latest", "base_latest"),
            ("dummy_save", "dummy_save"),
            ("ID1,2_paper", "ID1,2_paper"),
        ]
    )


class Filter(forms.Form):
    tags = forms.ChoiceField(label="Filter Tags")
    year = forms.ChoiceField(label="Filter Year")
    region = forms.ChoiceField(label="Filter Region")

    def __init__(self, *args, **kwargs):
        options = kwargs.pop("options", None)
        super().__init__(*args, **kwargs)
        if options:
            for filter, choice_list in options.items():
                self.fields[filter].choices = choice_list
