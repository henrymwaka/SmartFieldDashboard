from django.db import models

class TraitSchedule(models.Model):
    crop = models.CharField(max_length=100)
    trait = models.CharField(max_length=100)
    days_after_planting = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.crop} - {self.trait} ({self.days_after_planting} days)"
