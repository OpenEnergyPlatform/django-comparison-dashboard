from django import forms


class Scenario(forms.Form):
    scenario_choices = forms.MultipleChoiceField(choices=[('1', 'code_exposed_fig1'), ('2', 'base_latest'), ('3', 'dummy_save'), ('4', 'ID1,2_paper')])
