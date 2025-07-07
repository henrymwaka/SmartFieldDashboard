from django.db import models
from django.contrib.auth.models import User

class TraitSchedule(models.Model):
    crop = models.CharField(max_length=100)
    trait = models.CharField(max_length=100)
    days_after_planting = models.PositiveIntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.crop} - {self.trait} ({self.days_after_planting} days)"
class Sample(models.Model):
    sampleDbId = models.CharField(max_length=100, unique=True)
    sampleName = models.CharField(max_length=255)
    studyDbId = models.CharField(max_length=100, null=True, blank=True)
    observationUnitDbId = models.CharField(max_length=100, null=True, blank=True)
    germplasmDbId = models.CharField(max_length=100, null=True, blank=True)
    sampleType = models.CharField(max_length=100, default="Tissue")
    takenBy = models.CharField(max_length=100, null=True, blank=True)
    sampleTimestamp = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.sampleName
class Season(models.Model):
    seasonDbId = models.CharField(max_length=100, unique=True)
    season = models.CharField(max_length=100)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.season} {self.year}"

class ObservationLevel(models.Model):
    observationLevel = models.CharField(max_length=100, unique=True)
    levelName = models.CharField(max_length=100, blank=True)
    levelOrder = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.observationLevel


class TraitTimeline(models.Model):
    plant_id = models.CharField(max_length=100)
    trait = models.CharField(max_length=100)
    expected_date = models.DateField(null=True, blank=True)
    actual_date = models.DateField(null=True, blank=True)
    note = models.TextField(blank=True, null=True)
    status_flag = models.CharField(
        max_length=10,
        choices=[
            ('🕓', 'Too Early'),
            ('⏳', 'Due Soon'),
            ('❌', 'Overdue'),
            ('✔️', 'Completed')
        ],
        default='🕓'
    )
    updated_on = models.DateTimeField(auto_now=True)
    entered_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = ('plant_id', 'trait')

    def __str__(self):
        return f"{self.plant_id} - {self.trait} ({self.status_flag})"


class PlantTraitData(models.Model):
    plant_id = models.CharField(max_length=50)
    trait = models.CharField(max_length=100)
    value = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.plant_id} - {self.trait}: {self.value}"

class Germplasm(models.Model):
    germplasmDbId = models.CharField(max_length=50, unique=True)
    germplasmName = models.CharField(max_length=100)
    commonCropName = models.CharField(max_length=50, blank=True)
    genus = models.CharField(max_length=50, blank=True)
    species = models.CharField(max_length=50, blank=True)
    pedigree = models.TextField(blank=True)
    seedSource = models.CharField(max_length=100, blank=True)
    synonyms = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.germplasmName

class Trial(models.Model):
    trialDbId = models.CharField(max_length=100, unique=True)
    trialName = models.CharField(max_length=255)
    programName = models.CharField(max_length=255, blank=True, null=True)
    startDate = models.DateField(null=True, blank=True)
    endDate = models.DateField(null=True, blank=True)
    additionalInfo = models.JSONField(blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.trialName

class FieldPlot(models.Model):
    plant_id = models.CharField(max_length=50, unique=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, default='too-early')
    planting_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    trial = models.ForeignKey(Trial, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.plant_id} ({self.status})"

class PlantData(models.Model):
    plant_id = models.CharField(max_length=100, unique=True)
    planting_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.plant_id

class Program(models.Model):
    programDbId = models.AutoField(primary_key=True)
    programName = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50, blank=True, null=True)
    objective = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.programName
        
class Person(models.Model):
    name = models.CharField(max_length=100)
    orcid = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True, null=True)

class ObservationMethod(models.Model):
    methodName = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    className = models.CharField(max_length=100)

class Image(models.Model):
    imageName = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    imageFile = models.ImageField(upload_to='images/')
