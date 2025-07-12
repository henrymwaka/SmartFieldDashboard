# api/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),  # Just a test endpoint
]
from django.urls import path
from . import brapi_views

urlpatterns = [
    path("brapi/v2/calls", brapi_views.brapi_calls),
    path("brapi/v2/trials", brapi_views.brapi_trials),
    path("brapi/v2/studies", brapi_views.brapi_studies),
    path("brapi/v2/studies/<str:studyDbId>", brapi_views.brapi_study_detail),
    path("brapi/v2/studies/<str:studyDbId>/observationunits", brapi_views.brapi_study_observationunits),
    path("brapi/v2/germplasm", brapi_views.brapi_germplasm),
    path("brapi/v2/germplasm/<str:germplasmDbId>", brapi_views.brapi_germplasm_detail),
    path("brapi/v2/programs", brapi_views.brapi_programs),
    path("brapi/v2/seasons", brapi_views.brapi_seasons),
    path("brapi/v2/commoncropnames", brapi_views.brapi_commoncropnames),
    path("brapi/v2/locations", brapi_views.brapi_locations),
    path("brapi/v2/observationunits", brapi_views.brapi_observationunits),
    path("brapi/v2/observations", brapi_views.brapi_observations),
    path("brapi/v2/observationvariables", brapi_views.brapi_observationvariables),
    path("brapi/v2/observationlevels", brapi_views.brapi_observationlevels),
    path("brapi/v2/people", brapi_views.brapi_people),
    path("brapi/v2/observationmethods", brapi_views.brapi_observationmethods),
    path("brapi/v2/images", brapi_views.brapi_images),
    path("brapi/v2/samples", brapi_views.brapi_samples),
    path("brapi/v2/samples-search", brapi_views.brapi_samples),  # optional alias
    path("brapi/v2/samples", brapi_views.brapi_post_samples, name="post_samples"),  # for POST
    path("brapi/v2/observations", brapi_views.brapi_post_observations, name="post_observations"),  # for POST
]
