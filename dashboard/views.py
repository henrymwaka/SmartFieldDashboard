from django.shortcuts import render
from io import TextIOWrapper
from .models import TraitSchedule, PlantTraitData
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from .forms import BulkGPSAssignmentForm
from .models import FieldPlot
from django.contrib import messages
from django.shortcuts import redirect
import csv, json
from datetime import timedelta

# ✅ Home dashboard
@login_required
def index(request):
    return render(request, 'dashboard/index.html')

# ✅ Upload CSV with trait data and render dashboard
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

# ✅ Upload trait schedule CSV
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

# ✅ Export CSV of trait statuses
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

# ✅ Save edits directly to database (used in edit modal)
@csrf_exempt
@login_required
def save_trait_edits(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            edits = data.get("edits", {})

            for plant_id, traits in edits.items():
                for trait, value in traits.items():
                    if value.strip():
                        PlantTraitData.objects.update_or_create(
                            plant_id=plant_id,
                            trait=trait,
                            defaults={
                                "value": value.strip(),
                                "uploaded_by": request.user,
                            }
                        )

            return JsonResponse({"status": "success"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "invalid request"}, status=405)

# ✅ Update only session cache (optional)
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

# ✅ AJAX: Get trait history per plant
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

# ✅ Snapshot: HTML view of historical trait values
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

# ✅ Download snapshot as CSV
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

# ✅ Serve Field Visualization HTML
@login_required
def field_visualization_view(request):
    return render(request, 'dashboard/smartfield_field_visualization.html')

def field_map_view(request):
    return render(request, 'dashboard/field_map.html')

@login_required
def bulk_gps_assignment(request):
    if request.method == 'POST':
        form = BulkGPSAssignmentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            plot, created = FieldPlot.objects.update_or_create(
                plant_id=data['plant_id'],
                defaults={
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                    'status': data['status']
                }
            )
            messages.success(request, f"GPS data saved for {data['plant_id']}")
            return redirect('bulk_gps')
    else:
        form = BulkGPSAssignmentForm()

    return render(request, 'dashboard/bulk_gps.html', {'form': form})

@login_required
def trait_status_table(request):
    data = request.session.get('cached_data')
    trait_flags = request.session.get('cached_trait_flags')
    headers = ['plant_id'] + [t.trait for t in TraitSchedule.objects.all()]

    if not data or not trait_flags:
        return HttpResponse("No cached data found. Please upload trait data first.", status=400)

    table_rows = []
    for entry in data:
        pid = entry.get('plant_id')
        row = [pid] + [trait_flags.get(pid, {}).get(trait, '') for trait in headers[1:]]
        table_rows.append(row)

    return render(request, 'dashboard/trait_status_table.html', {
        'headers': headers,
        'table_rows': table_rows
    })




# ✅ API: GPS coordinates for field visualization
@require_GET
@login_required
def plot_coordinates_api(request):
    from .models import FieldPlot, PlantTraitData

    trait_map = {}
    for pt in PlantTraitData.objects.all():
        key = (pt.plant_id, pt.trait.lower())
        trait_map[key] = pt.value

    plots = FieldPlot.objects.all()
    data = []
    for p in plots:
        if p.latitude is not None and p.longitude is not None:
            data.append({
                "id": p.plant_id,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "status": p.status,
                "traits": {
                    "height": trait_map.get((p.plant_id, "height")),
                    "chlorophyll": trait_map.get((p.plant_id, "chlorophyll")),
                }
            })
    return JsonResponse({"plots": data})