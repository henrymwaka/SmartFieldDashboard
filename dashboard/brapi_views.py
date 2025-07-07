from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
#from .utils import brapi_paginate  # assumes you have a pagination helper
from .utils import apply_dynamic_filters
from rest_framework import status
import datetime
from django.utils.dateparse import parse_datetime
from .models import FieldPlot, PlantTraitData, Trial, TraitSchedule, Germplasm, Program, Person, ObservationMethod, Image, Sample
from .serializers import (
    ObservationSerializer,
    ObservationUnitSerializer,
    TrialSerializer,
    ObservationVariableSerializer,
    GermplasmSerializer,
    ProgramSerializer,
    PersonSerializer, ObservationMethodSerializer, ImageSerializer, SampleSerializer
)

@api_view(['POST'])
def brapi_post_observations(request):
    # Placeholder for now
    return Response({"message": "POST observations not yet implemented."}, status=status.HTTP_201_CREATED)


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
        {"call": "samples", "methods": ["GET"], "versions": ["2.0"]},
        


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
def brapi_observationlevels(request):
    levels = ObservationLevel.objects.all()
    serializer = ObservationLevelSerializer(levels, many=True)
    return Response({
        "metadata": {
            "pagination": {
                "page": 0,
                "pageSize": 100,
                "totalCount": levels.count(),
                "totalPages": 1
            }
        },
        "result": {"data": serializer.data}
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

@api_view(['POST'])
def brapi_post_samples(request):
    samples = request.data.get("samples", [])

    created = []
    errors = []

    for s in samples:
        sample_id = s.get("sampleDbId")
        observation_unit_id = s.get("observationUnitDbId")
        taken_date = s.get("takenDateTime")
        tissue_type = s.get("sampleType")
        description = s.get("notes", "")
        
        try:
            plot = FieldPlot.objects.get(plant_id=observation_unit_id)
        except FieldPlot.DoesNotExist:
            errors.append({"sampleDbId": sample_id, "error": "Observation unit not found"})
            continue

        try:
            taken_at = datetime.datetime.fromisoformat(taken_date.replace("Z", "+00:00"))
        except Exception:
            errors.append({"sampleDbId": sample_id, "error": "Invalid timestamp format"})
            continue

        sample_obj = Sample.objects.create(
            sampleDbId=sample_id,
            observationUnit=plot,
            takenDateTime=taken_at,
            sampleType=tissue_type,
            notes=description
        )
        created.append(str(sample_obj.id))

    return Response({
        "metadata": {
            "status": [{"message": f"{len(created)} samples recorded", "code": "201"}] + errors,
            "datafiles": []
        },
        "result": {
            "data": created
        }
    }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)


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
def brapi_people(request):
    people = Person.objects.all()
    serializer = PersonSerializer(people, many=True)
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(people),
                "currentPage": 0,
                "totalCount": len(people),
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
def brapi_observationmethods(request):
    methods = ObservationMethod.objects.all()
    serializer = ObservationMethodSerializer(methods, many=True)
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(methods),
                "currentPage": 0,
                "totalCount": len(methods),
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
def brapi_images(request):
    images = Image.objects.all()
    serializer = ImageSerializer(images, many=True)
    return Response({
        "metadata": {
            "pagination": {
                "pageSize": len(images),
                "currentPage": 0,
                "totalCount": len(images),
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

@api_view(['POST'])
def brapi_post_observations(request):
    observations = request.data.get("observations", [])

    created = []
    errors = []

    for obs in observations:
        unit_id = obs.get("observationUnitDbId")
        trait_id = obs.get("observationVariableDbId")
        value = obs.get("value")
        timestamp = obs.get("observationTimeStamp")

        try:
            plot = FieldPlot.objects.get(plant_id=unit_id)
        except FieldPlot.DoesNotExist:
            errors.append({"unit_id": unit_id, "error": "Observation unit not found"})
            continue

        try:
            trait = TraitSchedule.objects.get(id=trait_id)
        except TraitSchedule.DoesNotExist:
            errors.append({"trait_id": trait_id, "error": "Trait not found"})
            continue

        try:
            dt_obj = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception:
            errors.append({"timestamp": timestamp, "error": "Invalid ISO format"})
            continue

        obs_entry = PlantTraitData.objects.create(
            plant_id=unit_id,
            trait=trait.trait,
            value=value,
            recorded_at=dt_obj
        )
        created.append(str(obs_entry.id))

    return Response({
        "metadata": {
            "status": [{"message": f"{len(created)} observations recorded", "code": "201"}] + errors,
            "datafiles": []
        },
        "result": {
            "data": created
        }
    }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def brapi_post_samples(request):
    samples_data = request.data.get("samples", [])
    created = []
    errors = []

    for sample in samples_data:
        try:
            new_sample = Sample.objects.create(
                sampleName=sample.get("sampleName"),
                sampleDescription=sample.get("sampleDescription", ""),
                studyDbId=sample.get("studyDbId"),
                observationUnitDbId=sample.get("observationUnitDbId"),
                takenDateTime=sample.get("takenDateTime", None),
                sampleType=sample.get("sampleType", "TISSUE"),
                tissueType=sample.get("tissueType", "LEAF"),
                additionalInfo=sample.get("additionalInfo", {})
            )
            created.append(SampleSerializer(new_sample).data)
        except Exception as e:
            errors.append({"sample": sample.get("sampleName"), "error": str(e)})

    return Response({
        "metadata": {
            "status": [{"message": f"{len(created)} samples created", "code": "201"}] + errors,
            "datafiles": []
        },
        "result": {
            "data": created
        }
    }, status=status.HTTP_201_CREATED if created else status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def brapi_samples(request):
    samples = Sample.objects.all()

    # Define mapping from query param to model field
    field_mapping = {
        'sampleName': 'sampleName__icontains',
        'germplasmDbId': 'germplasmDbId',
        'studyDbId': 'studyDbId',
        'takenBy': 'takenBy__icontains',
        'sampleType': 'sampleType__icontains',
    }

    # Apply reusable dynamic filters
    samples = apply_dynamic_filters(samples, request.GET, field_mapping)

    # Apply date range filtering (sampleTimestamp)
    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    if start_date:
        parsed_start = parse_datetime(start_date)
        if parsed_start:
            samples = samples.filter(sampleTimestamp__gte=parsed_start)

    if end_date:
        parsed_end = parse_datetime(end_date)
        if parsed_end:
            samples = samples.filter(sampleTimestamp__lte=parsed_end)

    # Paginate manually if brapi_paginate is not available
    page = int(request.GET.get("page", 0))
    page_size = int(request.GET.get("pageSize", 1000))
    start = page * page_size
    end = start + page_size
    paginated_samples = samples[start:end]

    serialized_data = SampleSerializer(paginated_samples, many=True).data

    response_data = {
        "metadata": {
            "pagination": {
                "pageSize": page_size,
                "currentPage": page,
                "totalCount": samples.count(),
                "totalPages": (samples.count() + page_size - 1) // page_size
            },
            "status": [],
            "datafiles": []
        },
        "result": {
            "data": serialized_data
        }
    }

    return Response(response_data)

    # Apply reusable dynamic filters
    samples = apply_dynamic_filters(samples, request.GET, field_mapping)

    # Paginate manually if brapi_paginate is not available
    page = int(request.GET.get("page", 0))
    page_size = int(request.GET.get("pageSize", 1000))
    start = page * page_size
    end = start + page_size
    paginated_samples = samples[start:end]

    serializer = SampleSerializer(paginated_samples, many=True)
    metadata = {
        "pagination": {
            "pageSize": page_size,
            "currentPage": page,
            "totalCount": samples.count(),
            "totalPages": (samples.count() + page_size - 1) // page_size
        },
        "status": [],
        "datafiles": []
    }

    return Response({
        "metadata": metadata,
        "result": {"data": serializer.data}
    }, status=status.HTTP_200_OK)
