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
