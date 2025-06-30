from django.shortcuts import render
from io import TextIOWrapper
from .models import TraitSchedule
import csv
from datetime import timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def index(request):
    return render(request, 'dashboard/index.html')

@login_required
def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.reader(file)
        headers = next(reader)
        data = []
        planting_dates = {}
        trait_fields = [h for h in headers if h.lower() not in ['plant_id', 'block', 'row', 'column', 'planting_date']]

        for row in reader:
            entry = dict(zip(headers, row))
            data.append(entry)
            if entry.get("plant_id") and entry.get("planting_date"):
                try:
                    planting_dates[entry["plant_id"]] = timezone.datetime.strptime(entry["planting_date"], "%Y-%m-%d")
                except ValueError:
                    planting_dates[entry["plant_id"]] = None

        # Save trait values to database
        for entry in data:
            pid = entry.get("plant_id")
            for trait in trait_fields:
                value = entry.get(trait, '').strip()
                if value:
                    PlantTraitData.objects.create(
                        plant_id=pid,
                        trait=trait,
                        value=value,
                        uploaded_by=request.user
                    )

        # Trait schedule and visualization preparation
        trait_schedule = {t.trait: t.days_after_planting for t in TraitSchedule.objects.all()}
        today = timezone.now()

        trait_flags = {}
        trait_due_dates = {}
        trait_summary = {}

        complete, incomplete, empty = 0, 0, 0
        plot_labels, plot_data, plot_colors = [], [], []

        for entry in data:
            pid = entry.get("plant_id")
            completed = 0
            flags = {}
            due_map = {}

            for trait in trait_fields:
                value = entry.get(trait, '').strip()
                if value:
                    flags[trait] = '✔️'
                    completed += 1
                else:
                    due_day = trait_schedule.get(trait)
                    if due_day and pid in planting_dates and planting_dates[pid]:
                        expected_date = planting_dates[pid] + timedelta(days=due_day)
                        due_map[trait] = expected_date.strftime("%Y-%m-%d")

                        if today >= expected_date:
                            flags[trait] = '❌'
                        elif (expected_date - today).days <= 3:
                            flags[trait] = '⏳'
                        else:
                            flags[trait] = '🕓'
                    else:
                        flags[trait] = '🕓'

                trait_summary.setdefault(trait, {'✔️': 0, '⏳': 0, '❌': 0, '🕓': 0})
                trait_summary[trait][flags[trait]] += 1

            trait_flags[pid] = flags
            trait_due_dates[pid] = due_map

            total_traits = len(trait_fields)
            plot_labels.append(pid)
            plot_data.append(completed)

            if completed == total_traits:
                plot_colors.append("green")
                complete += 1
            elif completed == 0:
                plot_colors.append("red")
                empty += 1
            else:
                plot_colors.append("orange")
                incomplete += 1

        # Cache data for export
        request.session['cached_data'] = data
        request.session['cached_trait_flags'] = trait_flags

        return render(request, 'dashboard/index.html', {
            'headers': headers,
            'data': data,
            'trait_flags': trait_flags,
            'trait_due_dates': trait_due_dates,
            'trait_summary': trait_summary,
            'plot_labels': plot_labels,
            'plot_data': plot_data,
            'plot_colors': plot_colors,
            'summary_data': [complete, incomplete, empty],
        })

    return render(request, 'dashboard/upload.html')

@login_required
def upload_schedule_csv(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = TextIOWrapper(request.FILES['file'].file, encoding='utf-8')
        reader = csv.DictReader(file)
        TraitSchedule.objects.all().delete()
        for row in reader:
            TraitSchedule.objects.create(
                trait=row['trait'],
                days_after_planting=int(row['days_after_planting'])
            )
        return render(request, 'dashboard/upload.html', {'message': 'Schedule uploaded successfully!'})
    return render(request, 'dashboard/upload.html')

@login_required
def export_trait_status_csv(request):
    headers = ['plant_id'] + [t.trait for t in TraitSchedule.objects.all()]
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trait_status.csv"'

    writer = csv.writer(response)
    writer.writerow(headers)

    data = request.session.get('cached_data')
    trait_flags = request.session.get('cached_trait_flags')

    if not data or not trait_flags:
        return HttpResponse("No cached data found. Please upload CSV data first.", status=400)

    for entry in data:
        pid = entry.get('plant_id')
        row = [pid] + [trait_flags.get(pid, {}).get(h, '') for h in headers[1:]]
        writer.writerow(row)

    return response
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
@login_required
def save_trait_edits(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            edits = data.get("edits", {})
            # Optional: persist to DB instead of session
            cached_data = request.session.get('cached_data', [])
            for entry in cached_data:
                pid = entry.get("plant_id")
                if pid in edits:
                    entry.update(edits[pid])
            request.session['cached_data'] = cached_data
            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "invalid request"}, status=405)
@csrf_exempt
@login_required
def update_trait_value(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            plant_id = data.get('plant_id')
            trait = data.get('trait')
            new_value = data.get('value')

            # Update trait_flags session data
            trait_flags = request.session.get('cached_trait_flags', {})
            if plant_id in trait_flags and trait in trait_flags[plant_id]:
                trait_flags[plant_id][trait] = new_value
                request.session['cached_trait_flags'] = trait_flags

            # Update raw data so CSV export reflects edits
            cached_data = request.session.get('cached_data', [])
            for entry in cached_data:
                if entry.get('plant_id') == plant_id:
                    entry[trait] = new_value
            request.session['cached_data'] = cached_data

            return JsonResponse({'success': True, 'message': 'Trait updated'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)


