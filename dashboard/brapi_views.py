# dashboard/views.py (or your app's views.py)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework import status
import datetime

# Assuming these are in your_app/utils.py or similar
# from .utils import apply_dynamic_filters

# Simplified apply_dynamic_filters for demonstration if not already defined:
def apply_dynamic_filters(queryset, query_params, field_mapping):
    for param, field in field_mapping.items():
        value = query_params.get(param)
        if value:
            filter_kwargs = {field: value}
            queryset = queryset.filter(**filter_kwargs)
    return queryset

from dashboard.models import ( # Changed from .models to dashboard.models based on initial code
    ObservationVariable, PlantTraitData, Sample, Trial, Germplasm, FieldPlot,
    TraitSchedule, Program, Person, ObservationMethod, Image, ObservationLevel
)
from dashboard.serializers import ( # Changed from .serializers to dashboard.serializers
    ObservationSerializer, ObservationUnitSerializer, TrialSerializer,
    ObservationVariableSerializer, GermplasmSerializer, ProgramSerializer,
    PersonSerializer, ObservationMethodSerializer, ImageSerializer,
    SampleSerializer, ObservationLevelSerializer
)

def build_response(data, total_count, page=0, page_size=1000, status_messages=None, datafiles=None):
    """
    Helper function to build a consistent BrAPI response structure.
    """
    if status_messages is None:
        status_messages = []
    if datafiles is None:
        datafiles = []

    return Response({
        "metadata": {
            "pagination": {
                "pageSize": page_size,
                "currentPage": page,
                "totalCount": total_count,
                "totalPages": (total_count + page_size - 1) // page_size
            },
            "status": status_messages,
            "datafiles": datafiles
        },
        "result": {"data": data}
    })

# --- BrAPI Endpoints ---

@api_view(['GET'])
def brapi_calls(request):
    """
    Returns a list of supported BrAPI calls.
    """
    calls = [
        {"call": "trials", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observationvariables", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observationunits", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observations", "methods": ["GET", "POST"], "versions": ["2.0"]},
        {"call": "studies", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "germplasm", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "locations", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "commoncropnames", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "programs", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "studies/{studyDbId}/observationunits", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "germplasm/{germplasmDbId}", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "seasons", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "samples", "methods": ["GET", "POST"], "versions": ["2.0"]},
        {"call": "people", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observationmethods", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "images", "methods": ["GET"], "versions": ["2.0"]},
        {"call": "observationlevels", "methods": ["GET"], "versions": ["2.0"]},
    ]
    return Response({
        "metadata": {},
        "result": {"data": calls}
    })

@api_view(['GET'])
def brapi_trials(request):
    """
    Retrieves a list of trials with pagination.
    """
    trials = Trial.objects.all()
    page = int(request.GET.get('page', 0))
    page_size = int(request.GET.get('pageSize', 1000))

    paginator = Paginator(trials, page_size)
    try:
        paged_trials = paginator.page(page + 1) # Paginator pages are 1-indexed
    except Exception:
        return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

    data = TrialSerializer(paged_trials, many=True).data
    return build_response(data, paginator.count, page, page_size)

@api_view(['GET'])
def brapi_studies(request):
    """
    Retrieves a list of studies (trials) with detailed information.
    """
    studies_queryset = Trial.objects.all()
    page = int(request.GET.get('page', 0))
    page_size = int(request.GET.get('pageSize', 1000))

    paginator = Paginator(studies_queryset, page_size)
    try:
        paged_studies = paginator.page(page + 1)
    except Exception:
        return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

    data = []
    for trial in paged_studies:
        data.append({
            "studyDbId": str(trial.id), # Assuming 'id' is used for studyDbId as in the original first code
            "studyName": trial.trialName,
            "trialDbId": str(trial.trialDbId), # Keep trialDbId if it's distinct and needed
            "locationDbId": getattr(trial, 'locationDbId', "1"), # Assuming a field or default
            "locationName": getattr(trial, 'location', "Field 1"),
            "season": {
                "seasonDbId": str(trial.startDate.year) if trial.startDate else "unknown",
                "season": str(trial.startDate.year) if trial.startDate else "unknown"
            },
            "startDate": trial.startDate.isoformat() if trial.startDate else None,
            "endDate": trial.endDate.isoformat() if trial.endDate else None,
            "status": "active",
            "programDbId": getattr(trial, 'programDbId', ''),
            "programName": getattr(trial, 'programName', ''),
            "observationVariableDbIds": [], # Populate if available in Trial model
            "studyType": "field",
            "additionalInfo": getattr(trial, 'additionalInfo', {})
        })
    return build_response(data, paginator.count, page, page_size)

@api_view(['GET'])
def brapi_study_detail(request, studyDbId):
    """
    Retrieves details for a specific study by ID.
    """
    try:
        trial = Trial.objects.get(id=studyDbId) # Using 'id' as per the initial code's studyDbId mapping
    except Trial.DoesNotExist:
        return build_response([], 0, 0, 0, [{"message": f"Study with DbId={studyDbId} not found", "code": "404"}], status=status.HTTP_404_NOT_FOUND)

    result = {
        "studyDbId": str(trial.id),
        "studyName": trial.trialName,
        "trialDbId": str(trial.trialDbId),
        "locationDbId": getattr(trial, 'locationDbId', "1"),
        "locationName": getattr(trial, 'location', "Field 1"),
        "startDate": trial.startDate.isoformat() if trial.startDate else None,
        "endDate": trial.endDate.isoformat() if trial.endDate else None,
        "status": "active",
        "season": {
            "seasonDbId": str(trial.startDate.year) if trial.startDate else "unknown",
            "season": str(trial.startDate.year) if trial.startDate else "unknown"
        },
        "programDbId": getattr(trial, 'programDbId', ""),
        "programName": getattr(trial, 'programName', ""),
        "observationVariableDbIds": [],
        "studyType": "field",
        "additionalInfo": getattr(trial, 'additionalInfo', {})
    }
    return build_response(result, 1, 0, 1) # Single item, so totalCount is 1

@api_view(['GET'])
def brapi_observationvariables(request):
    """
    Retrieves a list of observation variables (traits) with pagination.
    """
    # Assuming TraitSchedule is the model for observation variables
    traits = TraitSchedule.objects.filter(active=True)
    page = int(request.GET.get('page', 0))
    page_size = int(request.GET.get('pageSize', 1000))

    paginator = Paginator(traits, page_size)
    try:
        paged_traits = paginator.page(page + 1)
    except Exception:
        return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

    data = ObservationVariableSerializer(paged_traits, many=True).data
    return build_response(data, paginator.count, page, page_size)

@api_view(['GET', 'POST'])
def brapi_observations(request):
    """
    Handles GET requests for observations (with filtering and pagination)
    and POST requests for creating new observations.
    """
    if request.method == 'GET':
        observations = PlantTraitData.objects.all()

        # Filtering
        field_mapping = {
            'observationUnitDbId': 'plant_id__icontains',
            'observationVariableDbId': 'trait__icontains', # Assuming trait name matches variable ID logic
        }
        observations = apply_dynamic_filters(observations, request.GET, field_mapping)

        # Date range filtering
        start_date = request.GET.get('observationTimeStampRangeStart')
        end_date = request.GET.get('observationTimeStampRangeEnd')

        if start_date:
            parsed_start = parse_datetime(start_date)
            if parsed_start:
                observations = observations.filter(recorded_at__gte=parsed_start) # Assuming 'recorded_at'
        if end_date:
            parsed_end = parse_datetime(end_date)
            if parsed_end:
                observations = observations.filter(recorded_at__lte=parsed_end)

        page = int(request.GET.get('page', 0))
        page_size = int(request.GET.get('pageSize', 1000))

        paginator = Paginator(observations, page_size)
        try:
            paged_obs = paginator.page(page + 1)
        except Exception:
            return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

        data = ObservationSerializer(paged_obs, many=True).data
        return build_response(data, paginator.count, page, page_size)

    elif request.method == 'POST':
        payload = request.data.get("observations", [])
        created_ids = []
        errors = []

        for obs in payload:
            unit_id = obs.get("observationUnitDbId")
            trait_variable_name = obs.get("observationVariableName")
            value = obs.get("value")
            timestamp = obs.get("observationTimeStamp")

            if not all([unit_id, trait_variable_name, value, timestamp]):
                errors.append({"observation": obs, "error": "Missing required fields"})
                continue

            try:
                # Find FieldPlot by plant_id for observationUnitDbId
                field_plot = FieldPlot.objects.get(plant_id=unit_id)
            except FieldPlot.DoesNotExist:
                errors.append({"observation": obs, "error": f"Observation unit {unit_id} not found"})
                continue

            try:
                # Find TraitSchedule by trait_name (or other identifier if available)
                # It's better to link to a TraitSchedule if possible, or ensure 'trait' in PlantTraitData
                # is consistent with ObservationVariable
                # For simplicity, assuming trait_variable_name can be directly used for 'trait' field
                pass # No direct TraitSchedule object needed for PlantTraitData if trait is just a string

            except Exception as e:
                errors.append({"observation": obs, "error": f"Error finding trait: {e}"})
                continue

            try:
                # Convert timestamp to datetime object
                dt_obj = datetime.datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                errors.append({"observation": obs, "error": f"Invalid timestamp format: {timestamp}"})
                continue

            try:
                # Use update_or_create to handle potential existing observations for the same unit/trait
                # This assumes a unique constraint or desired behavior for updates
                # If you always want to create new observations, use .create()
                obj, created = PlantTraitData.objects.update_or_create(
                    plant_id=unit_id,
                    trait=trait_variable_name, # Use the trait name
                    defaults={
                        "value": value,
                        "timestamp": dt_obj, # Use 'timestamp' if that's the field name
                        # "recorded_at": dt_obj, # Use 'recorded_at' if that's the field name
                    }
                )
                created_ids.append(str(obj.id))
            except Exception as e:
                errors.append({"observation": obs, "error": f"Database error: {e}"})

        status_messages = [{"message": f"{len(created_ids)} observations recorded successfully", "code": "201"}]
        if errors:
            status_messages.extend([{"message": err["error"], "code": "400", "details": err.get("observation")} for err in errors])

        return build_response(created_ids, len(created_ids), status_messages=status_messages, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)

@api_view(['GET'])
def brapi_observationunits(request):
    """
    Retrieves a list of observation units (FieldPlots) with pagination.
    """
    units = FieldPlot.objects.all()
    page = int(request.GET.get('page', 0))
    page_size = int(request.GET.get('pageSize', 1000))

    paginator = Paginator(units, page_size)
    try:
        paged_units = paginator.page(page + 1)
    except Exception:
        return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

    data = ObservationUnitSerializer(paged_units, many=True).data
    return build_response(data, paginator.count, page, page_size)

@api_view(['GET'])
def brapi_study_observationunits(request, studyDbId):
    """
    Retrieves observation units associated with a specific study.
    """
    try:
        trial = Trial.objects.get(id=studyDbId) # Using 'id' for trial lookup
    except Trial.DoesNotExist:
        return build_response([], 0, 0, 0, [{"message": f"Study with DbId={studyDbId} not found", "code": "404"}], status=status.HTTP_404_NOT_FOUND)

    units = FieldPlot.objects.filter(trial=trial)
    page = int(request.GET.get('page', 0))
    page_size = int(request.GET.get('pageSize', 1000))

    paginator = Paginator(units, page_size)
    try:
        paged_units = paginator.page(page + 1)
    except Exception:
        return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

    data = ObservationUnitSerializer(paged_units, many=True).data
    return build_response(data, paginator.count, page, page_size)

@api_view(['GET'])
def brapi_samples(request):
    """
    Retrieves a list of samples with filtering and pagination.
    """
    samples = Sample.objects.all()

    field_mapping = {
        'sampleName': 'sampleName__icontains',
        'germplasmDbId': 'germplasmDbId',
        'studyDbId': 'studyDbId',
        'takenBy': 'takenBy__icontains',
        'sampleType': 'sampleType__icontains',
    }
    samples = apply_dynamic_filters(samples, request.GET, field_mapping)

    start_date = request.GET.get('startDate')
    end_date = request.GET.get('endDate')

    if start_date:
        parsed_start = parse_datetime(start_date)
        if parsed_start:
            samples = samples.filter(takenDateTime__gte=parsed_start) # Assuming 'takenDateTime' for samples
    if end_date:
        parsed_end = parse_datetime(end_date)
        if parsed_end:
            samples = samples.filter(takenDateTime__lte=parsed_end)

    page = int(request.GET.get("page", 0))
    page_size = int(request.GET.get("pageSize", 1000))

    paginator = Paginator(samples, page_size)
    try:
        paged_samples = paginator.page(page + 1)
    except Exception:
        return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

    serialized_data = SampleSerializer(paged_samples, many=True).data
    return build_response(serialized_data, paginator.count, page, page_size)

@api_view(['POST'])
def brapi_post_samples(request):
    """
    Creates new samples from a POST request.
    """
    samples_data = request.data.get("samples", [])
    created_samples_data = []
    errors = []

    for sample_data in samples_data:
        try:
            # Ensure required fields are present
            required_fields = ["sampleName", "observationUnitDbId", "takenDateTime", "sampleType"]
            if not all(field in sample_data for field in required_fields):
                errors.append({"sample": sample_data.get("sampleName", "N/A"), "error": "Missing required fields"})
                continue

            # Look up related FieldPlot for observationUnitDbId
            observation_unit_db_id = sample_data.get("observationUnitDbId")
            try:
                observation_unit = FieldPlot.objects.get(plant_id=observation_unit_db_id)
            except FieldPlot.DoesNotExist:
                errors.append({"sample": sample_data.get("sampleName", "N/A"), "error": f"ObservationUnitDbId '{observation_unit_db_id}' not found"})
                continue

            # Parse takenDateTime
            taken_date_time_str = sample_data.get("takenDateTime")
            try:
                taken_date_time = datetime.datetime.fromisoformat(taken_date_time_str.replace("Z", "+00:00"))
            except ValueError:
                errors.append({"sample": sample_data.get("sampleName", "N/A"), "error": f"Invalid 'takenDateTime' format: {taken_date_time_str}"})
                continue

            new_sample = Sample.objects.create(
                sampleName=sample_data.get("sampleName"),
                sampleDescription=sample_data.get("sampleDescription", ""),
                studyDbId=sample_data.get("studyDbId"),
                observationUnitDbId=observation_unit_db_id, # Store the ID directly
                observationUnit=observation_unit, # Link to the actual object if needed by your model
                takenDateTime=taken_date_time,
                sampleType=sample_data.get("sampleType", "TISSUE"),
                tissueType=sample_data.get("tissueType", "LEAF"),
                additionalInfo=sample_data.get("additionalInfo", {})
            )
            created_samples_data.append(SampleSerializer(new_sample).data)
        except Exception as e:
            errors.append({"sample": sample_data.get("sampleName", "N/A"), "error": str(e)})

    status_messages = [{"message": f"{len(created_samples_data)} samples created successfully", "code": "201"}]
    if errors:
        status_messages.extend([{"message": err["error"], "code": "400", "details": err.get("sample")} for err in errors])

    return build_response(created_samples_data, len(created_samples_data), status_messages=status_messages, status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS)

@api_view(['GET'])
def brapi_germplasm(request):
    """
    Retrieves a list of germplasm with filtering and pagination.
    """
    queryset = Germplasm.objects.all()

    field_mapping = {
        'germplasmDbId': 'id', # Assuming 'id' is mapped to germplasmDbId in your serializer
        'accessionNumber': 'accessionNumber__icontains',
        'germplasmName': 'germplasmName__icontains',
        # Add more filters as needed
    }
    queryset = apply_dynamic_filters(queryset, request.GET, field_mapping)

    page = int(request.GET.get('page', 0))
    page_size = int(request.GET.get('pageSize', 1000))

    paginator = Paginator(queryset, page_size)
    try:
        paged_germplasm = paginator.page(page + 1)
    except Exception:
        return build_response([], 0, page, page_size, [{"message": "Invalid page number", "code": "400"}], status=status.HTTP_400_BAD_REQUEST)

    serializer = GermplasmSerializer(paged_germplasm, many=True)
    return build_response(serializer.data, paginator.count, page, page_size)

@api_view(['GET'])
def brapi_germplasm_detail(request, germplasmDbId):
    """
    Retrieves details for a specific germplasm by ID.
    """
    try:
        germplasm = Germplasm.objects.get(id=germplasmDbId)
    except Germplasm.DoesNotExist:
        return build_response({}, 0, 0, 0, [{"message": "Germplasm not found", "code": "404"}], status=status.HTTP_404_NOT_FOUND)

    serializer = GermplasmSerializer(germplasm)
    return build_response(serializer.data, 1, 0, 1)

@api_view(['GET'])
def brapi_locations(request):
    """
    Retrieves unique locations from FieldPlot data.
    """
    plots = FieldPlot.objects.exclude(location__isnull=True).exclude(location__exact='').distinct('location')
    
    unique_locations = []
    # Assign unique IDs if not naturally available
    for i, plot in enumerate(plots):
        unique_locations.append({
            "locationDbId": str(i + 1), # Assigning a simple sequential ID
            "locationName": plot.location,
            "latitude": str(plot.latitude) if plot.latitude else None,
            "longitude": str(plot.longitude) if plot.longitude else None,
            # Add other relevant location details from FieldPlot if available
        })

    total_count = len(unique_locations)
    page = int(request.GET.get('page', 0))
    page_size = int(request.GET.get('pageSize', 1000))

    # Manual pagination since we're building a list
    start_index = page * page_size
    end_index = start_index + page_size
    paginated_locations = unique_locations[start_index:end_index]

    return build_response(paginated_locations, total_count, page, page_size)

@api_view(['GET'])
def brapi_commoncropnames(request):
    """
    Retrieves distinct crop names from TraitSchedule.
    """
    crop_names = TraitSchedule.objects.values_list('crop', flat=True).distinct()
    data = list(crop_names)
    return build_response(data, len(data))

@api_view(['GET'])
def brapi_people(request):
    """
    Retrieves a list of people.
    """
    people = Person.objects.all()
    serializer = PersonSerializer(people, many=True)
    data = serializer.data
    return build_response(data, len(data))

@api_view(['GET'])
def brapi_observationmethods(request):
    """
    Retrieves a list of observation methods.
    """
    methods = ObservationMethod.objects.all()
    serializer = ObservationMethodSerializer(methods, many=True)
    data = serializer.data
    return build_response(data, len(data))

@api_view(['GET'])
def brapi_images(request):
    """
    Retrieves a list of images.
    """
    images = Image.objects.all()
    serializer = ImageSerializer(images, many=True)
    data = serializer.data
    return build_response(data, len(data))

@api_view(['GET'])
def brapi_programs(request):
    """
    Retrieves distinct program names from trials.
    """
    programs = Trial.objects.values_list('programName', flat=True).distinct()
    # Assign simple DbIds
    data = [{"programDbId": str(i + 1), "programName": name} for i, name in enumerate(programs)]
    return build_response(data, len(data))

@api_view(['GET'])
def brapi_seasons(request):
    """
    Retrieves unique seasons (years from trial start dates).
    """
    seasons = Trial.objects.exclude(startDate__isnull=True).values_list('startDate', flat=True)
    unique_years = sorted(list(set([d.year for d in seasons if d])))
    
    data = [
        {
            "seasonDbId": str(year),
            "season": str(year),
            "year": year
        }
        for year in unique_years
    ]
    return build_response(data, len(data))

@api_view(['GET'])
def brapi_observationlevels(request):
    """
    Retrieves observation levels.
    """
    levels = ObservationLevel.objects.all().order_by('level_order')
    serializer = ObservationLevelSerializer(levels, many=True)
    data = serializer.data
    return build_response(data, len(data))

@api_view(['GET'])
def brapi_genotypes(request):
    """
    Placeholder for genotypes endpoint.
    """
    return build_response([], 0)

@api_view(['GET'])
def brapi_phenotypes(request):
    """
    Placeholder for phenotypes endpoint.
    """
    return build_response([], 0)

@api_view(['POST'])
def brapi_studies_search(request):
    """
    Placeholder for studies search (POST).
    """
    # Implement filtering logic based on request.data for POST searches
    return build_response([], 0)