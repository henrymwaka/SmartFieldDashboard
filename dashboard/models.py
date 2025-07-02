from django.db import models
from django.contrib.auth.models import User

class TraitSchedule(models.Model):
    crop = models.CharField(max_length=100)
    trait = models.CharField(max_length=100)
    days_after_planting = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.crop} - {self.trait} ({self.days_after_planting} days)"

class PlantTraitData(models.Model):
    plant_id = models.CharField(max_length=50)
    trait = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plant_id} - {self.trait}: {self.value}"

class FieldPlot(models.Model):
    plant_id = models.CharField(max_length=50, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='too-early')  # cached or computed label
    planting_date = models.DateField(null=True, blank=True)  # ✅ Added for time-based reminders

    def __str__(self):
        return f"{self.plant_id} ({self.status})"
