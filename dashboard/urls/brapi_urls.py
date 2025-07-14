from django.urls import path
from dashboard import brapi_views

urlpatterns = [
    path('calls', brapi_views.brapi_calls, name='brapi_calls'),
    path('commoncropnames', brapi_views.brapi_commoncropnames, name='brapi_commoncropnames'),
    path('germplasm', brapi_views.brapi_germplasm, name='brapi_germplasm'),
    path('germplasm/<int:germplasmDbId>', brapi_views.brapi_germplasm_detail, name='brapi_germplasm_detail'),
    path('locations', brapi_views.brapi_locations, name='brapi_locations'),
    path('observationunits', brapi_views.brapi_observationunits, name='brapi_observationunits'),
    path('observationvariables', brapi_views.brapi_observationvariables, name='brapi_observationvariables'),
    path('observations', brapi_views.brapi_observations, name='brapi_observations'),
    path('programs', brapi_views.brapi_programs, name='brapi_programs'),
    path('studies', brapi_views.brapi_studies, name='brapi_studies'),
    path('studies/<str:studyDbId>', brapi_views.brapi_study_detail, name='brapi_study_detail'),
    path('studies/<str:studyDbId>/observationunits', brapi_views.brapi_study_observationunits, name='brapi_study_observationunits'),
    path('trials', brapi_views.brapi_trials, name='brapi_trials'),
    path('genotypes', brapi_views.brapi_genotypes, name='brapi_genotypes'),
    path('phenotypes', brapi_views.brapi_phenotypes, name='brapi_phenotypes'),
    path('studies-search', brapi_views.brapi_studies_search, name='brapi_studies_search'),
    path('seasons', brapi_views.brapi_seasons, name='brapi_seasons'),
    path('samples', brapi_views.brapi_samples, name='brapi_samples'),
    path('observationlevels', brapi_views.brapi_observationlevels, name='brapi_observationlevels'),
    path('people', brapi_views.brapi_people, name='brapi_people'),
    path('observationmethods', brapi_views.brapi_observationmethods, name='brapi_observationmethods'),
    path('images', brapi_views.brapi_images, name='brapi_images'),
]
