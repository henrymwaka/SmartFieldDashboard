from django.shortcuts import render
from django.http import HttpResponseRedirect
import csv
from io import TextIOWrapper

def index(request):
    return render(request, 'dashboard/index.html')

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        data = []
        file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.reader(file)
        headers = next(reader)
        for row in reader:
            data.append(dict(zip(headers, row)))
        return render(request, 'dashboard/index.html', {'data': data, 'headers': headers})
    return render(request, 'dashboard/upload.html')
