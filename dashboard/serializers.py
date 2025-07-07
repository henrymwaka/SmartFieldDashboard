from rest_framework import serializers
from .models import (
    FieldPlot,
    Germplasm,
    PlantTraitData,
    Program,
    Sample,
    Season,
    TraitSchedule,
    Trial,
    ObservationLevel,
    Person,
    ObservationMethod,
    Image,
)

# ───────────────────────────────
# Location & Program Serializers
# ───────────────────────────────

class LocationSerializer(serializers.Serializer):
    locationDbId = serializers.IntegerField()
    locationName = serializers.CharField()
    latitude = serializers.FloatField(allow_null=True)
    longitude = serializers.FloatField(allow_null=True)


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = ['programDbId', 'programName', 'abbreviation', 'objective']


# ───────────────────────────────
# Observation & Plot Serializers
# ───────────────────────────────

class ObservationLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObservationLevel
        fields = ['observationLevel', 'levelName', 'levelOrder']


class ObservationSerializer(serializers.ModelSerializer):
    observationDbId = serializers.CharField(source='id')
    observationUnitDbId = serializers.CharField(source='plant_id')
    traitName = serializers.CharField(source='trait')
    value = serializers.CharField()

    class Meta:
        model = PlantTraitData
        fields = ['observationDbId', 'observationUnitDbId', 'traitName', 'value']


class ObservationUnitSerializer(serializers.ModelSerializer):
    observationUnitDbId = serializers.CharField(source='plant_id')
    location = serializers.SerializerMethodField()
    plantingDate = serializers.DateField(source='planting_date', allow_null=True)

    class Meta:
        model = FieldPlot
        fields = ['observationUnitDbId', 'location', 'plantingDate']

    def get_location(self, obj):
        if obj.latitude is not None and obj.longitude is not None:
            return {
                "geometry": {
                    "type": "Point",
                    "coordinates": [obj.longitude, obj.latitude]
                }
            }
        return None


# ───────────────────────────────
# Trial & Germplasm Serializers
# ───────────────────────────────

class TrialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trial
        fields = [
            'trialDbId', 'trialName', 'programName',
            'startDate', 'endDate', 'additionalInfo'
        ]


class GermplasmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Germplasm
        fields = '__all__'


# ───────────────────────────────
# Sample & Season Serializers
# ───────────────────────────────

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'


class SeasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Season
        fields = '__all__'


# ───────────────────────────────
# Trait (Observation Variable)
# ───────────────────────────────

class ObservationVariableSerializer(serializers.Serializer):
    observationVariableDbId = serializers.CharField(source='id')
    traitName = serializers.CharField(source='trait')
    crop = serializers.CharField()
    status = serializers.BooleanField(source='active')

    def to_representation(self, instance):
        """BrAPI-compliant trait representation."""
        data = super().to_representation(instance)
        data.update({
            "observationVariableName": instance.trait,
            "synonyms": [],
            "ontologyDbId": "",
            "ontologyName": "",
            "ontologyReference": "",
            "defaultValue": "",
            "scale": {"scaleName": "Nominal"},
            "method": {"methodName": "Field Observation"},
            "trait": {
                "traitDbId": str(instance.id),
                "traitName": instance.trait,
                "traitClass": "phenological",
                "attribute": "",
                "entity": "",
                "status": "active" if instance.active else "inactive"
            }
        })
        return data


# ───────────────────────────────
# Person Serializer
# ───────────────────────────────

class PersonSerializer(serializers.ModelSerializer):
    personDbId = serializers.CharField(source='id')

    class Meta:
        model = Person
        fields = [
            'personDbId', 'firstName', 'lastName', 'middleName',
            'initials', 'name', 'email', 'phoneNumber',
            'address', 'instituteName', 'organizationName', 'type'
        ]


# ───────────────────────────────
# Observation Method Serializer
# ───────────────────────────────

class ObservationMethodSerializer(serializers.ModelSerializer):
    observationMethodDbId = serializers.CharField(source='id')

    class Meta:
        model = ObservationMethod
        fields = [
            'observationMethodDbId', 'observationMethodName', 'methodClass',
            'description', 'formula', 'bibliographicReference'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["ontologyReference"] = {
            "ontologyDbId": "",
            "ontologyName": "",
            "version": "",
            "documentationURL": ""
        }
        return data


# ───────────────────────────────
# Image Serializer
# ───────────────────────────────

class ImageSerializer(serializers.ModelSerializer):
    imageDbId = serializers.CharField(source='id')

    class Meta:
        model = Image
        fields = [
            'imageDbId', 'imageFileName', 'imageName', 'description',
            'copyright', 'fileSize', 'mimeType', 'imageFileURL',
            'scale', 'timeStamp', 'takenBy', 'uploadedBy',
            'observationUnitDbId', 'additionalInfo'
        ]
