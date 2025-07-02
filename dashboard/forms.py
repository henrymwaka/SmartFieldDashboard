# dashboard/forms.py
from django import forms
from .models import FieldPlot, PlantTraitData

class FieldPlotForm(forms.ModelForm):
    class Meta:
        model = FieldPlot
        fields = ['plant_id', 'latitude', 'longitude', 'status']

class BulkGPSAssignmentForm(forms.Form):
    plant_id = forms.ChoiceField(choices=[])
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)
    status = forms.ChoiceField(choices=[
        ('completed', 'Completed'),
        ('due-soon', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('too-early', 'Too Early'),
    ], required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        plant_ids = PlantTraitData.objects.values_list('plant_id', flat=True).distinct()
        self.fields['plant_id'].choices = [(pid, pid) for pid in plant_ids]
