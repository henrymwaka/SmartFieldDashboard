from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.contrib import messages
from io import TextIOWrapper
from datetime import timedelta
from django.utils.dateparse import parse_date
import csv, json

from .models import TraitSchedule, PlantTraitData, FieldPlot, PlantData, TraitTimeline
from .forms import BulkGPSAssignmentForm

# -----------------------------
# 1. HOME DASHBOARD
# -----------------------------

@login_required
def index(request):
    return render(request, 'dashboard/index.html')

# -----------------------------
# 2. CSV UPLOAD VIEWS
# -----------------------------

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

        trait_schedule = {t.trait: t.days_after_planting for t in TraitSchedule.objects.all()}
        today = timezone.now()
        trait_flags, trait_due_dates, trait_summary = {}, {}, {}
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
                        flags[trait] = '❌' if today >= expected_date else ('⏳' if (expected_date - today).days <= 3 else '🕓')
                    else:
                        flags[trait] = '🕓'

                trait_summary.setdefault(trait, {'✔️': 0, '⏳': 0, '❌': 0, '🕓': 0})
                trait_summary[trait][flags[trait]] += 1

            trait_flags[pid] = flags
            trait_due_dates[pid] = due_map
            total_traits = len(trait_fields)
            plot_labels.append(pid)
            plot_data.append(completed)
            plot_colors.append("green" if completed == total_traits else ("red" if completed == 0 else "orange"))
            complete += (completed == total_traits)
            empty += (completed == 0)
            incomplete += (0 < completed < total_traits)

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

# -----------------------------
# 3. CSV EXPORT
# -----------------------------

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

# -----------------------------
# 4. TRAIT EDITING & SESSION UPDATES
# -----------------------------

@csrf_exempt
@login_required
def save_trait_edits(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            for plant_id, traits in data.get("edits", {}).items():
                for trait, value in traits.items():
                    if value.strip():
                        PlantTraitData.objects.update_or_create(
                            plant_id=plant_id,
                            trait=trait,
                            defaults={"value": value.strip(), "uploaded_by": request.user}
                        )
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

            trait_flags = request.session.get('cached_trait_flags', {})
            if plant_id in trait_flags and trait in trait_flags[plant_id]:
                trait_flags[plant_id][trait] = new_value
                request.session['cached_trait_flags'] = trait_flags

            cached_data = request.session.get('cached_data', [])
            for entry in cached_data:
                if entry.get('plant_id') == plant_id:
                    entry[trait] = new_value
            request.session['cached_data'] = cached_data

            return JsonResponse({'success': True, 'message': 'Trait updated'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)

# -----------------------------
# 5. TRAIT HISTORY & SNAPSHOT
# -----------------------------

@require_GET
@login_required
def plant_trait_history(request, plant_id):
    traits = PlantTraitData.objects.filter(plant_id=plant_id).order_by('-timestamp')
    grouped = {}
    for t in traits:
        grouped.setdefault(t.trait, []).append({
            "value": t.value,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M"),
            "user": t.uploaded_by.username if t.uploaded_by else "unknown"
        })
    return JsonResponse({"plant_id": plant_id, "traits": grouped})


@require_GET
@login_required
def plant_snapshot(request, plant_id):
    traits = PlantTraitData.objects.filter(plant_id=plant_id).order_by('trait', '-timestamp')
    grouped = {}
    for t in traits:
        grouped.setdefault(t.trait, []).append({
            "value": t.value,
            "timestamp": t.timestamp.strftime("%Y-%m-%d %H:%M"),
            "user": t.uploaded_by.username if t.uploaded_by else "unknown"
        })
    return render(request, 'dashboard/snapshot.html', {
        "plant_id": plant_id,
        "grouped_traits": grouped
    })


@require_GET
@login_required
def download_plant_history_csv(request, plant_id):
    traits = PlantTraitData.objects.filter(plant_id=plant_id).order_by('trait', '-timestamp')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{plant_id}_trait_history.csv"'
    writer = csv.writer(response)
    writer.writerow(['Trait', 'Value', 'Timestamp', 'Uploaded By'])
    for t in traits:
        writer.writerow([
            t.trait,
            t.value,
            t.timestamp.strftime('%Y-%m-%d %H:%M'),
            t.uploaded_by.username if t.uploaded_by else 'unknown'
        ])
    return response

# -----------------------------
# 6. GPS VIEWS
# -----------------------------

@login_required
def field_visualization_view(request):
    return render(request, 'dashboard/smartfield_field_visualization.html')

@login_required
def field_map_view(request):
    return render(request, 'dashboard/field_map.html')

@login_required
def bulk_gps_assignment(request):
    if request.method == 'POST':
        form = BulkGPSAssignmentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            FieldPlot.objects.update_or_create(
                plant_id=data['plant_id'],
                defaults={'latitude': data['latitude'], 'longitude': data['longitude'], 'status': data['status']}
            )
            messages.success(request, f"GPS data saved for {data['plant_id']}")
            return redirect('bulk_gps')
    else:
        form = BulkGPSAssignmentForm()
    return render(request, 'dashboard/bulk_gps.html', {'form': form})

@require_GET
@login_required
def plot_coordinates_api(request):
    trait_map = {(pt.plant_id, pt.trait.lower()): pt.value for pt in PlantTraitData.objects.all()}
    plots = FieldPlot.objects.all()
    data = [{
        "id": p.plant_id,
        "latitude": p.latitude,
        "longitude": p.longitude,
        "status": p.status,
        "traits": {
            "height": trait_map.get((p.plant_id, "height")),
            "chlorophyll": trait_map.get((p.plant_id, "chlorophyll")),
        }
    } for p in plots if p.latitude is not None and p.longitude is not None]
    return JsonResponse({"plots": data})

# -----------------------------
# 7. TRAIT TABLE & HEATMAP
# -----------------------------

@login_required
def trait_status_table(request):
    data = request.session.get('cached_data')
    trait_flags = request.session.get('cached_trait_flags')
    headers = ['plant_id'] + [t.trait for t in TraitSchedule.objects.all()]
    if not data or not trait_flags:
        return HttpResponse("No cached data found. Please upload trait data first.", status=400)

    table_rows = [[entry.get('plant_id')] + [trait_flags.get(entry.get('plant_id'), {}).get(trait, '') for trait in headers[1:]] for entry in data]
    return render(request, 'dashboard/trait_status_table.html', {'headers': headers, 'table_rows': table_rows})

@login_required
def trait_heatmap_view(request):
    data = request.session.get('cached_data', [])
    trait_flags = request.session.get('cached_trait_flags', {})
    headers = list(data[0].keys()) if data else []
    return render(request, 'dashboard/trait_heatmap.html', {'headers': headers, 'data': data, 'trait_flags': trait_flags})

# -----------------------------
# 8. PLANTING DATES EDITORS
# -----------------------------

@login_required
def planting_dates_view(request):
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("plant_"):
                plant_id = key.split("plant_")[1]
                try:
                    plant = PlantData.objects.get(plant_id=plant_id)
                    plant.planting_date = value if value else None
                    plant.save()
                except PlantData.DoesNotExist:
                    continue
        return redirect("planting_dates")
    plants = PlantData.objects.all().order_by("plant_id")
    return render(request, "dashboard/planting_dates.html", {"plants": plants})

@login_required
def plot_planting_dates(request):
    if request.method == 'POST':
        for key, value in request.POST.items():
            if key.startswith('planting_date_'):
                plot_id = key.replace('planting_date_', '')
                try:
                    plot = FieldPlot.objects.get(plant_id=plot_id)
                    plot.planting_date = parse_date(value)
                    plot.save()
                except FieldPlot.DoesNotExist:
                    continue
        return redirect('plot_planting_dates')

    plots = FieldPlot.objects.all().order_by('plant_id')
    return render(request, 'dashboard/planting_dates.html', {'plots': plots})
   
# -----------------------------
# 9. Reminder Dashboard View
# -----------------------------
@login_required
def trait_reminder_dashboard(request):
    timelines = TraitTimeline.objects.all().order_by('plant_id', 'trait')
    plant_trait_map = {}

    for entry in timelines:
        plant_id = entry.plant_id
        trait = entry.trait
        flag = entry.status_flag
        plant_trait_map.setdefault(plant_id, {})[trait] = flag

    trait_list = sorted(set(t.trait for t in timelines))
    plant_ids = sorted(plant_trait_map.keys())

    return render(request, 'dashboard/trait_reminder_dashboard.html', {
        'trait_list': trait_list,
        'plant_trait_map': plant_trait_map,
        'plant_ids': plant_ids,
    })