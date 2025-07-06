from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from .models import FieldPlot, PlantTraitData, Trial, TraitSchedule, Germplasm, Program
from .serializers import (
    ObservationSerializer,
    ObservationUnitSerializer,
    TrialSerializer,
    ObservationVariableSerializer,
    GermplasmSerializer,
    ProgramSerializer
)


@api_view(['GET'])
def brapi_calls(request):
    calls = [
        {"call": "trials", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observationvariables", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observationunits", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observations", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "studies", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "germplasm", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "locations", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "commoncropnames", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "programs", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "studies/{studyDbId}/observationunits", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "germplasm/{germplasmDbId}", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "seasons", "methods": ["GET"], "versions": ["2.0"]},

    ]
    return Response({
        "metadata": {},
        "result": {
            "data": calls
        }
    })


@api_view(['GET'])
def brapi_trials(request):
    trials = Trial.objects.all()
    paginator = Paginator(trials, 1000)
    page = request.GET.get('page', 1)
    paged_trials = paginator.get_page(page)

    data = TrialSerializer(paged_trials, many=True).data
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 1000,
                "currentPage": int(page),
                "totalCount": paginator.count,
                "totalPages": paginator.num_pages
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": data
        }
    })


@api_view(['GET'])
def brapi_studies(request):
    studies = []
    for trial in Trial.objects.all():
        studies.append({
            "studyDbId": str(trial.trialDbId),
            "studyName": trial.trialName,
            "trialDbId": str(trial.trialDbId),
            "locationDbId": "1",
            "locationName": trial.location if hasattr(trial, 'location') else "Field 1",
            "season": {
                "seasonDbId": trial.startDate.year if trial.startDate else "unknown",
                "season": str(trial.startDate.year) if trial.startDate else "unknown"
            },
            "startDate": str(trial.startDate),
            "endDate": str(trial.endDate),
            "status": "active"
        })

    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(studies),
                "currentPage": 0,
                "totalCount": len(studies),
                "totalPages": 1
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": studies
        }
    })

@api_view(['GET'])
def brapi_genotypes(request):
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 0,
                "currentPage": 0,
                "totalCount": 0,
                "totalPages": 0
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": []
        }
    })


@api_view(['GET'])
def brapi_phenotypes(request):
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 0,
                "currentPage": 0,
                "totalCount": 0,
                "totalPages": 0
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": []
        }
    })


@api_view(['POST'])
def brapi_studies_search(request):
    # Later: You can parse POST parameters to filter real studies
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 0,
                "currentPage": 0,
                "totalCount": 0,
                "totalPages": 0
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": []
        }
    })

@api_view(['GET'])
def brapi_observationvariables(request):
    traits = TraitSchedule.objects.filter(active=True)
    serializer = ObservationVariableSerializer(traits, many=True)
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 1000,
                "currentPage": 1,
                "totalCount": len(serializer.data),
                "totalPages": 1
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": serializer.data
        }
    })


@api_view(['GET'])
def brapi_observations(request):
    observations = PlantTraitData.objects.all()
    plant_id = request.GET.get('observationUnitDbId')
    trait = request.GET.get('traitName')
    if plant_id:
        observations = observations.filter(plant_id__icontains=plant_id)
    if trait:
        observations = observations.filter(trait__icontains=trait)

    paginator = Paginator(observations, 1000)
    page = request.GET.get('page', 1)
    paged_obs = paginator.get_page(page)

    data = ObservationSerializer(paged_obs, many=True).data
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 1000,
                "currentPage": int(page),
                "totalCount": paginator.count,
                "totalPages": paginator.num_pages
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": data
        }
    })


@api_view(['GET'])
def brapi_observationunits(request):
    units = FieldPlot.objects.all()
    paginator = Paginator(units, 1000)
    page = request.GET.get('page', 1)
    paged_units = paginator.get_page(page)

    data = ObservationUnitSerializer(paged_units, many=True).data
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 1000,
                "currentPage": int(page),
                "totalCount": paginator.count,
                "totalPages": paginator.num_pages
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": data
        }
    })


@api_view(['GET'])
def brapi_study_observationunits(request, studyDbId):
    try:
        trial = Trial.objects.get(trialDbId=studyDbId)
    except Trial.DoesNotExist:
        return Response({
            "metadata": {
                "status": [{"message": f"Study with trialDbId={studyDbId} not found", "code": "404"}],
                "pagination": {"pageSize": 0, "currentPage": 0, "totalCount": 0, "totalPages": 0},
                "datafiles": []
            },
            "result": {"data": []}
        }, status=404)

    units = FieldPlot.objects.filter(trial=trial)
    paginator = Paginator(units, 1000)
    page = request.GET.get('page', 1)
    paged_units = paginator.get_page(page)

    data = ObservationUnitSerializer(paged_units, many=True).data
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 1000,
                "currentPage": int(page),
                "totalCount": paginator.count,
                "totalPages": paginator.num_pages
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": data
        }
    })


@api_view(['GET'])
def brapi_germplasm(request):
    queryset = Germplasm.objects.all()
    germplasm_id = request.GET.get('germplasmDbId')
    accession_number = request.GET.get('accessionNumber')
    if germplasm_id:
        queryset = queryset.filter(id=germplasm_id)
    if accession_number:
        queryset = queryset.filter(accessionNumber__icontains=accession_number)

    paginator = Paginator(queryset, 1000)
    page = request.GET.get('page', 1)
    paged = paginator.get_page(page)

    serializer = GermplasmSerializer(paged, many=True)
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": 1000,
                "currentPage": int(page),
                "totalCount": paginator.count,
                "totalPages": paginator.num_pages
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": serializer.data
        }
    })


@api_view(['GET'])
def brapi_germplasm_detail(request, germplasmDbId):
    try:
        germplasm = Germplasm.objects.get(id=germplasmDbId)
    except Germplasm.DoesNotExist:
        return Response({
            "metadata": {
                "status": [{"message": "Germplasm not found", "code": "404"}],
                "datafiles": []
            },
            "result": {}
        }, status=404)

    serializer = GermplasmSerializer(germplasm)
    return Response({
        "metadata": {
            "status": [],
            "datafiles": []
        },
        "result": serializer.data
    })


@api_view(['GET'])
def brapi_study_detail(request, studyDbId):
    try:
        trial = Trial.objects.get(trialDbId=studyDbId)
    except Trial.DoesNotExist:
        return Response({
            "metadata": {
                "status": [{"message": "Study not found", "code": "404"}],
                "datafiles": []
            },
            "result": {}
        }, status=404)

    result = {
        "studyDbId": str(trial.trialDbId),
        "studyName": trial.trialName,
        "trialDbId": str(trial.trialDbId),
        "locationDbId": "1",
        "locationName": getattr(trial, 'location', "Field 1"),
        "startDate": str(trial.startDate),
        "endDate": str(trial.endDate),
        "status": "active",
        "season": {
            "seasonDbId": trial.startDate.year if trial.startDate else "unknown",
            "season": str(trial.startDate.year) if trial.startDate else "unknown"
        },
        "programDbId": "",
        "programName": trial.programName or "",
        "observationVariableDbIds": [],
        "studyType": "field",
        "additionalInfo": trial.additionalInfo if hasattr(trial, 'additionalInfo') else {}
    }

    return Response({
        "metadata": {
            "status": [],
            "datafiles": []
        },
        "result": result
    })


@api_view(['GET'])      
def brapi_locations(request):
    plots = FieldPlot.objects.exclude(location__isnull=True).exclude(location__exact='')
    unique_locations = {}
    for plot in plots:
        key = plot.location.strip().lower()
        if key not in unique_locations:
            unique_locations[key] = {
                "locationDbId": len(unique_locations) + 1,
                "locationName": plot.location,
                "latitude": plot.latitude,
                "longitude": plot.longitude
            }

    data = list(unique_locations.values())
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(data),
                "currentPage": 0,
                "totalCount": len(data),
                "totalPages": 1
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": data
        }
    })


@api_view(['GET'])
def brapi_commoncropnames(request):
    crop_names = TraitSchedule.objects.values_list('crop', flat=True).distinct()
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(crop_names),
                "currentPage": 0,
                "totalCount": len(crop_names),
                "totalPages": 1
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": list(crop_names)
        }
    })


@api_view(['GET'])
def brapi_programs(request):
    programs = Trial.objects.values_list('programName', flat=True).distinct()
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(programs),
                "currentPage": 0,
                "totalCount": len(programs),
                "totalPages": 1
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": [{"programDbId": i + 1, "programName": name} for i, name in enumerate(programs)]
        }
    })
@api_view(['GET'])
def brapi_seasons(request):
    seasons = Trial.objects.exclude(startDate__isnull=True).values_list('startDate', flat=True)
    unique_years = sorted(set([d.year for d in seasons if d]))
    
    data = [
        {
            "seasonDbId": str(year),
            "season": str(year),
            "year": year
        }
        for year in unique_years
    ]

    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(data),
                "currentPage": 0,
                "totalCount": len(data),
                "totalPages": 1
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": data
        }
    })
