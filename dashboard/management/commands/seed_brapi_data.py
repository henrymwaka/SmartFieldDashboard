"""
dashboard.management.commands.seed_brapi_data

Command to seed BRAPI‑compliant demo data:
    python manage.py seed_brapi_data --fieldmap fieldmap.csv --traitdefs traits.csv --traitvalues trait_values.csv

All arguments are optional. Supply any combination.
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date

from dashboard.models import FieldPlot, PlantTraitData, ObservationVariable


class Command(BaseCommand):
    help = (
        "Seed BRAPI‑compliant demo data from CSV files.\n\n"
        "--fieldmap     CSV with plant_id, latitude, longitude, status, planting_date, location\n"
        "--traitdefs    CSV with trait definitions (trait, method, class, scale, description)\n"
        "--traitvalues  CSV with trait observations (plant_id, trait, value, status_flag)\n\n"
        "Example: python manage.py seed_brapi_data --fieldmap map.csv --traitdefs traits.csv --traitvalues values.csv"
    )

    def add_arguments(self, parser):
        parser.add_argument("--fieldmap", type=str, help="Path to field‑map CSV")
        parser.add_argument("--traitdefs", type=str, help="Path to trait definitions CSV")
        parser.add_argument("--traitvalues", type=str, help="Path to trait values CSV")

    def handle(self, *args, **opts):
        did_something = False

        if path := opts.get("fieldmap"):
            self.load_fieldmap(Path(path))
            did_something = True

        if path := opts.get("traitdefs"):
            self.load_trait_definitions(Path(path))
            did_something = True

        if path := opts.get("traitvalues"):
            self.load_trait_values(Path(path))
            did_something = True

        if not did_something:
            self.stdout.write(self.style.WARNING(
                "⚠️ Nothing to do – specify at least one of --fieldmap / --traitdefs / --traitvalues."
            ))

    def load_fieldmap(self, path: Path) -> None:
        count = 0
        try:
            with path.open(newline="", encoding="utf-8-sig") as fh:
                reader = csv.DictReader(fh)
                reader.fieldnames = [h.strip() for h in reader.fieldnames]
                for row in reader:
                    FieldPlot.objects.update_or_create(
                        plant_id=row["plant_id"].strip(),
                        defaults={
                            "latitude": float(row.get("latitude", 0) or 0),
                            "longitude": float(row.get("longitude", 0) or 0),
                            "status": row.get("status", "too-early").strip(),
                            "planting_date": parse_date(row.get("planting_date", "").strip()) or None,
                            "location": row.get("location", "").strip(),
                        },
                    )
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ FieldPlot: {count} rows loaded from {path}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"❌ FieldPlot import failed: {exc}"))

    def load_trait_definitions(self, path: Path) -> None:
        count = 0
        try:
            with path.open(newline="", encoding="utf-8-sig") as fh:
                reader = csv.DictReader(fh)
                reader.fieldnames = [h.strip() for h in reader.fieldnames]
                for row in reader:
                    ObservationVariable.objects.update_or_create(
                        trait_name=row["trait"].strip(),
                        defaults={
                            "method": row.get("method", "").strip(),
                            "class_field": row.get("class", "").strip(),
                            "scale": row.get("scale", "").strip(),
                            "description": row.get("description", "").strip(),
                        },
                    )
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Trait definitions: {count} rows loaded from {path}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"❌ Trait definition import failed: {exc}"))

    def load_trait_values(self, path: Path) -> None:
        count = 0
        try:
            with path.open(newline="", encoding="utf-8-sig") as fh:
                reader = csv.DictReader(fh)
                reader.fieldnames = [h.strip() for h in reader.fieldnames]
                for row in reader:
                    PlantTraitData.objects.update_or_create(
                        plant_id=row["plant_id"].strip(),
                        trait=row["trait"].strip(),
                        defaults={
                            "value": row["value"].strip(),
                            "status_flag": row.get("status_flag", "🕓").strip(),
                        },
                    )
                    count += 1
            self.stdout.write(self.style.SUCCESS(f"✅ Trait values: {count} rows loaded from {path}"))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"❌ Trait value import failed: {exc}"))
