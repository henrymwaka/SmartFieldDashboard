try:
    from .brapi_views import urlpatterns  # type: ignore
except Exception:
    urlpatterns = []
