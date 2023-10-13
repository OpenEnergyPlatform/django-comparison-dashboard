from django import forms

from . import settings


class DataSourceUploadForm(forms.Form):
    """Default upload form for a data source"""

    scenario_id = forms.CharField(max_length=255)
    data_type = forms.ChoiceField(choices=[(dt.name, dt.name) for dt in settings.DataType])


class CSVSourceUploadForm(DataSourceUploadForm):
    """Upload form for CSV data source"""

    csv_file = forms.FileField()
