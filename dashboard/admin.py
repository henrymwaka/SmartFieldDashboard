from django.contrib import admin
from .models import (
    TraitSchedule, TraitTimeline, PlantTraitData, FieldPlot, Trial,
    Germplasm, ObservationLevel, Sample, Season, Program,
    Person, ObservationMethod, Image
)
import csv
from django.http import HttpResponse
from rangefilter.filters import DateRangeFilter
from django.contrib import admin
from django.http import HttpResponse
import csv

from .models import TraitTimeline

@admin.register(TraitTimeline)
class TraitTimelineAdmin(admin.ModelAdmin):
    list_display = (
        'plant_id', 'trait', 'expected_date', 'actual_date',
        'status_flag', 'entered_by', 'updated_on', 'note'
    )
    list_filter = (
        'trait',
        'status_flag',
        'entered_by',
        ('expected_date', DateRangeFilter),
    )
    search_fields = ('plant_id__plant_id', 'trait', 'note')
    date_hierarchy = 'expected_date'
    readonly_fields = ('updated_on',)
    ordering = ('expected_date',)
    list_per_page = 25
    actions = ['export_as_csv', 'mark_as_completed']

    fieldsets = (
        (None, {
            'fields': ('plant_id', 'trait', 'expected_date', 'actual_date', 'note')
        }),
        ('Status & Audit Trail', {
            'fields': ('status_flag', 'entered_by', 'updated_on'),
        }),
    )

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=trait_timeline.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export selected as CSV"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status_flag='❌')
        self.message_user(request, f"{updated} record(s) marked as ❌ (completed).")

    mark_as_completed.short_description = "Mark selected as ❌ (completed)"


@admin.register(TraitSchedule)
class TraitScheduleAdmin(admin.ModelAdmin):
    list_display = ('crop', 'trait', 'days_after_planting', 'active')
    list_filter = ('crop', 'active')
    search_fields = ('trait',)
    ordering = ('crop', 'days_after_planting')
    list_per_page = 25

@admin.register(PlantTraitData)
class PlantTraitDataAdmin(admin.ModelAdmin):
    list_display = ('plant_id', 'trait', 'value', 'uploaded_by', 'timestamp')
    list_filter = ('trait', 'uploaded_by')
    search_fields = ('plant_id', 'trait')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)
    list_per_page = 25

@admin.register(FieldPlot)
class FieldPlotAdmin(admin.ModelAdmin):
    list_display = ('plant_id', 'latitude', 'longitude', 'status', 'planting_date')
    search_fields = ('plant_id',)
    list_filter = ('status',)
    ordering = ('plant_id',)
    list_per_page = 25

@admin.register(Trial)
class TrialAdmin(admin.ModelAdmin):
    list_display = ('trialDbId', 'trialName', 'programName', 'startDate', 'endDate')
    search_fields = ('trialDbId', 'trialName')
    list_filter = ('programName',)
    ordering = ('startDate',)
    list_per_page = 25

@admin.register(Germplasm)
class GermplasmAdmin(admin.ModelAdmin):
    list_display = ('germplasmDbId', 'germplasmName', 'species', 'seedSource')
    search_fields = ('germplasmDbId', 'germplasmName')
    list_filter = ('species',)
    ordering = ('germplasmName',)
    list_per_page = 25

@admin.register(ObservationLevel)
class ObservationLevelAdmin(admin.ModelAdmin):
    list_display = ('level_name', 'level_order')
    ordering = ('level_order',)
    search_fields = ('level_name',)
    list_per_page = 25

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('sampleDbId', 'sampleName', 'sampleType', 'takenBy', 'sampleTimestamp')
    search_fields = ('sampleDbId', 'sampleName')
    list_filter = ('sampleType',)
    readonly_fields = ('sampleTimestamp',)
    ordering = ('-sampleTimestamp',)
    list_per_page = 25
    fieldsets = (
        (None, {
            'fields': ('sampleDbId', 'sampleName', 'sampleType', 'takenBy')
        }),
        ('Timestamp', {
            'fields': ('sampleTimestamp',),
        }),
    )

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('seasonDbId', 'season', 'year')
    search_fields = ('seasonDbId', 'season')
    list_filter = ('year',)
    ordering = ('-year',)
    list_per_page = 25

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ('programDbId', 'programName', 'abbreviation')
    search_fields = ('programName', 'abbreviation')
    ordering = ('programName',)
    list_per_page = 25

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('name', 'orcid', 'role')
    search_fields = ('name', 'role')
    ordering = ('name',)
    list_per_page = 25

@admin.register(ObservationMethod)
class ObservationMethodAdmin(admin.ModelAdmin):
    list_display = ('methodName', 'className')
    search_fields = ('methodName', 'className')
    list_per_page = 25

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('imageName', 'description')
    search_fields = ('imageName',)
    list_per_page = 25
