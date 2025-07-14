# =============================================================================
# SmartField Dashboard Views
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Imports
# -----------------------------------------------------------------------------

# --- Built-in modules ---
import csv
import datetime
import io
import json
import tempfile
import traceback
from datetime import timedelta
from io import TextIOWrapper
from collections import defaultdict # Added for trait_heatmap_view

# --- Django core ---
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage, send_mail
from django.core.paginator import Paginator
from django.db.models import Q, F, Value # F and Value added for trait_heatmap_view
from django.db.models.functions import Coalesce # Coalesce added for trait_heatmap_view
from django.http import HttpResponse, JsonResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.template.loader import render_to_string, get_template
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt    
from django.views.decorators.http import require_GET, require_http_methods, require_POST

# --- Third-party libraries ---
from weasyprint import HTML
from xhtml2pdf import pisa
import requests # Added for test_brapi_api

# --- Local app imports ---
from .forms import BulkGPSAssignmentForm, CustomUserCreationForm, TraitStatusUploadForm
from .models import FieldPlot, PlantData, PlantTraitData, TraitSchedule, TraitTimeline
from .utils import calculate_trait_reminder_status


# ----------------------------------------------------------------------------
# User Registration and Logout
# ----------------------------------------------------------------------------

def custom_logout(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Require email confirmation and admin approval
            user.save()

            # Email token + activation link
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activate_url = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )

            # Load email template and send
            subject = 'Confirm Your SmartField Registration'
            message = render_to_string('dashboard/account_activation_email.html', {
                'user': user,
                'activate_url': activate_url
            })

            email = EmailMessage(
                subject,
                message,
                to=[user.email],
                cc=['smartfield3@gmail.com'],  # Admin receives a copy
            )
            email.content_subtype = "html"
            email.send()

            messages.success(request, "Registration successful. Please check your email to confirm your address.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'dashboard/register.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.info(request, 'Account already activated.')
        else:
            messages.success(request, 'Email confirmed. Please wait for admin approval.')
        return redirect('login')
    else:
        messages.error(request, 'Activation link is invalid or expired.')
        return redirect('login')
@user_passes_test(lambda u: u.is_superuser or u.is_staff)
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'dashboard/user_management.html', {'users': users})

@user_passes_test(lambda u: u.is_superuser)
@login_required
def user_management(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    elif status_filter == 'staff':
        users = users.filter(is_staff=True)

    paginator = Paginator(users.order_by('-date_joined'), 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/user_management.html', {
        'users': page_obj,
        'query': query,
        'status_filter': status_filter,
        'page_obj': page_obj
    })

# ----------------------------------------------------------------------------
# Main Dashboard Views
# ----------------------------------------------------------------------------

@login_required
def index(request):
    messages.success(request, "Welcome to the SmartField Dashboard!")
    return render(request, 'dashboard/index.html')
@user_passes_test(lambda u: u.is_superuser)
@require_POST
@csrf_exempt
def update_user_from_modal(request):
    user_id = request.POST.get('user_id')
    username = request.POST.get('username')
    email = request.POST.get('email')
    is_active = request.POST.get('is_active') == 'true'
    is_staff = request.POST.get('is_staff') == 'true'
    is_superuser = request.POST.get('is_superuser') == 'true'

    try:
        user = User.objects.get(id=user_id)
        user.username = username
        user.email = email
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()
        return JsonResponse({'success': True, 'message': 'User updated successfully.'})
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
@login_required
def upload_trait_status_csv(request):
    if request.method == "POST":
        form = TraitStatusUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                try:
                    obj = PlantTraitData.objects.get(
                        plant_id__plant_id=row["plant_id"],
                        trait=row["trait"]
                    )
                    obj.actual_date = row.get("actual_date") or None
                    obj.status_flag = row.get("status_flag", obj.status_flag)
                    obj.note = row.get("note", obj.note)
                    obj.save()
                except PlantTraitData.DoesNotExist:
                    continue  # Optionally log missing rows

            messages.success(request, "Trait status CSV uploaded successfully.")
            return redirect("trait_status_table")
    else:
        form = TraitStatusUploadForm()

    return render(request, "dashboard/upload_trait_status.html", {"form": form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def user_management(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    users = User.objects.all()
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    if status_filter:
        if status_filter == 'active':
            users = users.filter(is_active=True)
        elif status_filter == 'inactive':
            users = users.filter(is_active=False)
        elif status_filter == 'staff':
            users = users.filter(is_staff=True)

    users = users.order_by('-date_joined')
    return render(request, 'dashboard/user_management.html', {'users': users, 'query': query, 'status_filter': status_filter})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_user_status(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        users = User.objects.filter(id__in=user_ids)

        if action == 'activate':
            users.update(is_active=True)
            messages.success(request, f"{users.count()} user(s) activated.")
        elif action == 'deactivate':
            users.update(is_active=False)
            messages.success(request, f"{users.count()} user(s) deactivated.")
        elif action == 'delete':
            count = users.count()
            users.delete()
            messages.success(request, f"{count} user(s) deleted.")

    return redirect('user_management')

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
                        expected_date_naive = planting_dates[pid] + timedelta(days=due_day)
                        expected_date = timezone.make_aware(expected_date_naive)
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

        TraitTimeline.objects.all().delete()
        for pid, planting_date in planting_dates.items():
            if not planting_date:
                continue
            for trait, days_after in trait_schedule.items():
                expected_date = timezone.make_aware(planting_date + timedelta(days=days_after))
                TraitTimeline.objects.update_or_create(
                    plant_id=pid,
                    trait=trait,
                    defaults={
                        'expected_date': expected_date,
                        'actual_date': None,
                        'status_flag': trait_flags.get(pid, {}).get(trait, '🕓'),
                        'note': '',
                        'entered_by': request.user
                    }
                )

        messages.success(request, 'Trait data uploaded successfully!')
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
@require_http_methods(["POST"])
def upload_snapshot_csv(request, plant_id):
    file = request.FILES.get("csv_file")
    if not file:
        return HttpResponse("No file uploaded", status=400)

    try:
        decoded = TextIOWrapper(file.file, encoding='utf-8')
        reader = csv.DictReader(decoded)

        for row in reader:
            trait = row.get("Trait")
            value = row.get("Value", "").strip()
            if trait and value:
                PlantTraitData.objects.update_or_create(
                    plant_id=plant_id,
                    trait=trait,
                    defaults={"value": value, "uploaded_by": request.user}
                )
        messages.success(request, "Trait values updated from CSV.")
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)

    return redirect("plant_snapshot", plant_id=plant_id)
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
        messages.success(request, 'Schedule uploaded successfully!')
        return redirect('upload_schedule')

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
@login_required
@csrf_exempt
def upload_brapi_data_view(request):
    if request.method == 'POST':
        fieldmap_file = request.FILES.get('fieldmap')
        traits_file = request.FILES.get('traits')

        if not fieldmap_file or not traits_file:
            messages.error(request, "Both files are required.")
            return redirect('upload_brapi_data')

        try:
            fieldmap_content = fieldmap_file.read().decode('utf-8')
            traits_content = traits_file.read().decode('utf-8')
            process_csv_files(fieldmap_content, traits_content)
            messages.success(request, "BrAPI data uploaded successfully.")
        except Exception as e:
            messages.error(request, f"Error processing files: {e}")

        return redirect('upload_brapi_data')

    return render(request, 'dashboard/upload_brapi_data.html')

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

@login_required
@require_http_methods(["GET"])
def edit_traits_view(request):
    data = request.session.get("cached_data", [])
    trait_flags = request.session.get("cached_trait_flags", {})

    if not data or not trait_flags:
        return HttpResponse("No cached trait data available. Please upload first.", status=400)

    trait_names = [h for h in data[0].keys() if h.lower() not in ["plant_id", "block", "row", "column", "planting_date"]]
    plant_ids = list(trait_flags.keys())

    return render(request, "dashboard/edit_traits.html", {
        "trait_names": trait_names,
        "plant_ids": plant_ids,
        "trait_flags": trait_flags
    })

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

    table_rows = []
    for entry in data:
        pid = entry.get('plant_id')
        row = [pid] + [trait_flags.get(pid, {}).get(trait, '🕓') for trait in headers[1:]]
        table_rows.append(row)

    zipped_rows = [zip(headers, row) for row in table_rows]

    return render(request, 'dashboard/trait_status_table.html', {
        'headers': headers,
        'zipped_rows': zipped_rows,
    })

# ──────────────────────────────────────────────────────────────────────────────
# 1️⃣  Trait-Heatmap View  (fully rewritten, syntax-error-free & optimised)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def trait_heatmap_view(request):
    """
    Build the {plant_id: {trait: flag}} map in a single DB hit, with the
    fallback of 🕓 (Too Early) handled in SQL via Coalesce.
    """
    # Query once – annotate missing flags with the literal 🕓
    records = (
        PlantTraitData.objects
        .values("plant_id", "trait")
        .annotate(flag=Coalesce(F("status_flag"), Value("🕓")))
    )

    # Build nested dict and collect all trait names
    trait_flags = defaultdict(dict)
    trait_set   = set()
    for rec in records:
        pid, trait, flag = rec["plant_id"], rec["trait"], rec["flag"]
        trait_flags[pid][trait] = flag
        trait_set.add(trait)

    headers = ["PlantID", *sorted(trait_set)]    # first column header + traits
    # The JS template only needs headers and trait_flags, but we keep data for completeness
    data = []

    context = {
        "headers": json.dumps(headers),
        "data": json.dumps(data),
        "trait_flags": json.dumps(trait_flags),
    }
    return render(request, "dashboard/trait_heatmap.html", context)

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
    trait_reminders = []

    for entry in timelines:
        plant_id = entry.plant_id
        trait = entry.trait
        expected = entry.expected_date
        actual = entry.actual_date
        status = calculate_trait_reminder_status(expected, actual)

        # Update matrix display
        plant_trait_map.setdefault(plant_id, {})[trait] = status

        # Add to reminder list
        trait_reminders.append({
            'plot': plant_id,
            'trait': trait,
            'status': status,
            'expected_date': expected,
            'actual_date': actual,
            'note': entry.note,
        })

    trait_list = sorted(set(t.trait for t in timelines))
    plant_ids = sorted(plant_trait_map.keys())
    return render(request, 'dashboard/trait_reminder_dashboard.html', {
        'trait_list': trait_list,
        'plant_trait_map': plant_trait_map,
        'plant_ids': plant_ids,
        'trait_reminders': trait_reminders,
    })
# -----------------------------
# 10. Export views
# -----------------------------

@login_required
def export_trait_reminders_pdf(request):
    timelines = TraitTimeline.objects.all().order_by('plant_id', 'trait')
    plant_trait_map = {}
    trait_reminders = []

    for entry in timelines:
        plant_id = entry.plant_id
        trait = entry.trait
        expected = entry.expected_date
        actual = entry.actual_date
        status = calculate_trait_reminder_status(expected, actual)

        plant_trait_map.setdefault(plant_id, {})[trait] = status
        trait_reminders.append({
            'plot': plant_id,
            'trait': trait,
            'status': status,
            'expected_date': expected,
            'actual_date': actual,
            'note': entry.note,
        })

    trait_list = sorted(set(t.trait for t in timelines))
    plant_ids = sorted(plant_trait_map.keys())

    context = {
        'trait_list': trait_list,
        'plant_trait_map': plant_trait_map,
        'plant_ids': plant_ids,
        'trait_reminders': trait_reminders,
    }

    template = get_template('dashboard/trait_reminder_pdf.html')
    html_content = template.render(context)

    with tempfile.NamedTemporaryFile(delete=True, suffix='.pdf') as output:
        HTML(string=html_content).write_pdf(output.name)
        output.seek(0)
        return HttpResponse(output.read(), content_type='application/pdf')


# ──────────────────────────────────────────────────────────────────────────────
# 2️⃣  Trait-Status PDF Export  (remove bad select_related on CharFields)
# ──────────────────────────────────────────────────────────────────────────────
@login_required
def export_trait_status_pdf(request):
    # CharFields are NOT relations → select_related('plant_id') would crash
    trait_data = PlantTraitData.objects.all()

    html_string = render_to_string(
        "dashboard/trait_status_pdf.html",
        {"data": trait_data},
    )
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="trait_status_report.pdf"'
    )
    return response

@login_required
def export_trait_pdf(request):
    traits = TraitTimeline.objects.values_list('trait', flat=True).distinct()
    plants = TraitTimeline.objects.values_list('plant_id', flat=True).distinct()

    data = []
    for plant_id in plants:
        row = {"plant_id": plant_id, "traits": {}}
        for trait in traits:
            record = TraitTimeline.objects.filter(plant_id=plant_id, trait=trait).first()
            row["traits"][trait] = record.status_flag if record else "-"
        data.append(row)

    html = render_to_string("dashboard/pdf_trait_report.html", {
        "generated_on": datetime.datetime.now(),
        "plant_traits": data,
        "trait_names": traits,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="trait_status_report.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response
@login_required
def download_snapshot_pdf(request, plant_id):
    traits = PlantTraitData.objects.filter(plant_id=plant_id).order_by('trait', '-timestamp')
    grouped = {}
    for t in traits:
        grouped.setdefault(t.trait, []).append({
            "value": t.value,
            "timestamp": t.timestamp.strftime('%Y-%m-%d %H:%M'),
            "user": t.uploaded_by.username if t.uploaded_by else "unknown"
        })

    context = {
        "plant_id": plant_id,
        "grouped_traits": grouped,
    }
    template = get_template("dashboard/plant_snapshot_pdf.html")
    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="snapshot_{plant_id}.pdf"'
    pisa.CreatePDF(io.StringIO(html), dest=response)
    return response

# -----------------------------
# 11. Mail
# -----------------------------

@login_required
def test_email(request):
    try:
        send_mail(
            subject='SmartField Email Test',
            message='This is a test email from SmartField.',
            from_email=None,
            recipient_list=['shaykins@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse("Test email sent.")
    except Exception as e:
        traceback.print_exc()  # This prints the error in the terminal
        return HttpResponseServerError(f"Email failed: {str(e)}")
def custom_logout(request):
    logout(request)
    return redirect('login')  # or any page you want
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/register.html', {'form': form})

def test_brapi_api(request):
    token_url = 'http://127.0.0.1:8000/o/token/'
    client_id = '1'
    client_secret = 'dxzWBEsknGFy3Z0pNknrbOpwapjhwBfX6HzUhI3VpiQG46mYKsDBRSNHMeHO4D2mXFbeiRJDwMwtCf4yGM95HNmDFUBQLVw4cNBn2X9iDOkVaYP2Z2IBwFalYWBiOmZV'
    username = 'shaykins'
    password = 'Klaisy&20'

    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        'client_id': client_id,
        'client_secret': client_secret,
    }

    token_response = requests.post(token_url, data=data)

    if token_response.status_code != 200:
        return JsonResponse({'error': 'Failed to get token', 'details': token_response.json()})

    access_token = token_response.json().get('access_token')
    headers = {'Authorization': f'Bearer {access_token}'}

    brapi_url = 'http://127.0.0.1:8000/brapi/v2/observationvariables'
    api_response = requests.get(brapi_url, headers=headers)

    return JsonResponse(api_response.json(), safe=False)

@csrf_exempt
def update_actual_date_ajax(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            plant_id = data.get('plant_id')
            trait = data.get('trait')
            new_date = data.get('actual_date')

            trait_entry = TraitTimeline.objects.get(plant_id_id=plant_id, trait=trait)
            trait_entry.actual_date = datetime.strptime(new_date, "%Y-%m-%d").date()
            trait_entry.save()

            return JsonResponse({"message": "Actual date updated successfully"})
        except TraitTimeline.DoesNotExist:
            return JsonResponse({"error": "Trait entry not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)