from django.shortcuts import render
from io import TextIOWrapper
from .models import TraitSchedule
import csv
from datetime import datetime, timedelta

def index(request):
    return render(request, 'dashboard/index.html')

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.reader(file)
        headers = next(reader)
        data = []
        planting_dates = {}
        trait_fields = [h for h in headers if h.lower() not in ['plant_id', 'block', 'row', 'column', 'planting_date']]

        # Load planting dates and raw data
        for row in reader:
            entry = dict(zip(headers, row))
            data.append(entry)
            if entry.get("plant_id") and entry.get("planting_date"):
                try:
                    planting_dates[entry["plant_id"]] = datetime.strptime(entry["planting_date"], "%Y-%m-%d")
                except ValueError:
                    planting_dates[entry["plant_id"]] = None

        # Load trait schedule from DB
        trait_schedule = {t.trait: t.days_after_planting for t in TraitSchedule.objects.all()}

        today = datetime.today()
        trait_flags = {}

        complete, incomplete, empty = 0, 0, 0
        plot_labels, plot_data, plot_colors = [], [], []

        for entry in data:
            pid = entry.get("plant_id")
            completed = 0
            flags = {}

            for trait in trait_fields:
                value = entry.get(trait, '').strip()
                if value:
                    flags[trait] = '✔️'
                    completed += 1
                else:
                    due_day = trait_schedule.get(trait)
                    if due_day and pid in planting_dates and planting_dates[pid]:
                        expected_date = planting_dates[pid] + timedelta(days=due_day)
                        if today >= expected_date:
                            flags[trait] = '❌'
                        elif (expected_date - today).days <= 3:
                            flags[trait] = '⏳'
                        else:
                            flags[trait] = '🕓'
                    else:
                        flags[trait] = '🕓'  # fallback if date/schedule is missing

            trait_flags[pid] = flags
            plot_labels.append(pid)
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
            'trait_flags': trait_flags,
            'plot_labels': plot_labels,
            'plot_data': plot_data,
            'plot_colors': plot_colors,
            'summary_data': [complete, incomplete, empty],
        })

    return render(request, 'dashboard/upload.html')

def upload_schedule_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.DictReader(file)
        TraitSchedule.objects.all().delete()
        for row in reader:
            TraitSchedule.objects.create(trait=row['trait'], days_after_planting=int(row['days_after_planting']))
    return render(request, 'dashboard/upload.html', {'message': 'Schedule uploaded successfully!'})
