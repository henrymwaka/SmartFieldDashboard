# api/views.py

from django.http import JsonResponse

def ping(request):
    return JsonResponse({'message': 'SmartField API is live ✅'})
