# dashboard/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import FieldPlot, PlantTraitData

# =============================================================================
# 1. Custom User Registration Form
# =============================================================================

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional'
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        help_text='Optional'
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        help_text='Required. Enter a valid email address.'
    )

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2'
        )


# =============================================================================
# 2. Field Plot Model Form
# =============================================================================

class FieldPlotForm(forms.ModelForm):
    class Meta:
        model = FieldPlot
        fields = ['plant_id', 'latitude', 'longitude', 'status']


# =============================================================================
# 3. Bulk GPS Assignment Form
# =============================================================================

class BulkGPSAssignmentForm(forms.Form):
    plant_id = forms.ChoiceField(choices=[])
    latitude = forms.FloatField(required=False)
    longitude = forms.FloatField(required=False)
    status = forms.ChoiceField(
        choices=[
            ('completed', 'Completed'),
            ('due-soon', 'Due Soon'),
            ('overdue', 'Overdue'),
            ('too-early', 'Too Early'),
        ],
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        plant_ids = PlantTraitData.objects.values_list('plant_id', flat=True).distinct()
        self.fields['plant_id'].choices = [(pid, pid) for pid in plant_ids]
