from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

# api/views.py
def ping(request):
    return JsonResponse({'message': 'SmartField API is live ✅'})


@method_decorator(csrf_exempt, name='dispatch')
class ODKXSyncReceiver(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            # TODO: Store data into appropriate models
            return JsonResponse({"status": "success", "message": "Data received."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
