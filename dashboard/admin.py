from django.contrib import admin
from .models import TraitSchedule, PlantTraitData, FieldPlot, Trial, Germplasm

@admin.register(TraitSchedule)
class TraitScheduleAdmin(admin.ModelAdmin):
    list_display = ('crop', 'trait', 'days_after_planting', 'active')
    list_filter = ('crop', 'active')
    search_fields = ('trait',)

@admin.register(PlantTraitData)
class PlantTraitDataAdmin(admin.ModelAdmin):
    list_display = ('plant_id', 'trait', 'value', 'uploaded_by', 'timestamp')
    list_filter = ('trait', 'uploaded_by')
    search_fields = ('plant_id', 'trait')

@admin.register(FieldPlot)
class FieldPlotAdmin(admin.ModelAdmin):
    list_display = ('plant_id', 'latitude', 'longitude', 'status')
    search_fields = ('plant_id',)
    list_filter = ('status',)

@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ('trialDbId', 'trialName', 'programName', 'startDate', 'endDate')
    search_fields = ('trialDbId', 'trialName')

@admin.register(Germplasm)
class GermplasmAdmin(admin.ModelAdmin):
    list_display = ('germplasmDbId', 'germplasmName', 'species', 'seedSource')
    search_fields = ('germplasmDbId', 'germplasmName')
