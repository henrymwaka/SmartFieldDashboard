from django.shortcuts import render
from io import TextIOWrapper
import csv

def index(request):
    return render(request, 'dashboard/index.html')

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.reader(file)
        headers = next(reader)
        data, plot_labels, plot_data, plot_colors = [], [], [], []

        complete, incomplete, empty = 0, 0, 0
        trait_fields = [h for h in headers if h.lower() not in ['plant_id', 'block', 'row', 'column']]

        for row in reader:
            entry = dict(zip(headers, row))
            data.append(entry)

            plot_id = entry.get('plant_id') or f"Plot {len(plot_labels)+1}"
            completed = sum(1 for t in trait_fields if entry.get(t, '').strip() != '')

            plot_labels.append(plot_id)
            plot_data.append(completed)
            total_traits = len(trait_fields)

            if completed == total_traits:
                plot_colors.append("green")
                complete += 1
            elif completed == 0:
                plot_colors.append("red")
                empty += 1
            else:
                plot_colors.append("orange")
                incomplete += 1

        return render(request, 'dashboard/index.html', {
            'headers': headers,
            'data': data,
            'plot_labels': plot_labels,
            'plot_data': plot_data,
            'plot_colors': plot_colors,
            'summary_data': [complete, incomplete, empty],
        })

    return render(request, 'dashboard/upload.html')
