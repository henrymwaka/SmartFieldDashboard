from django.core.management.base import BaseCommand
from dashboard.models import TraitSchedule, FieldPlot, PlantTraitData, TraitTimeline
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Sends trait data entry reminders by updating TraitTimeline entries'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        trait_schedule = {t.trait: t.days_after_planting for t in TraitSchedule.objects.all()}
        trait_fields = list(trait_schedule.keys())
        
        self.stdout.write("Updating trait timelines...")
        TraitTimeline.objects.all().delete()

        for plot in FieldPlot.objects.all():
            if not plot.planting_date:
                continue
            for trait in trait_fields:
                due_day = trait_schedule.get(trait)
                if due_day is None:
                    continue
                expected_date = plot.planting_date + timedelta(days=due_day)

                flag = '🕓'  # Default
                if PlantTraitData.objects.filter(plant_id=plot.plant_id, trait=trait).exists():
                    flag = '✔️'
                elif today >= expected_date:
                    flag = '❌'
                elif (expected_date - today).days <= 3:
                    flag = '⏳'

                TraitTimeline.objects.update_or_create(
                    plant_id=plot.plant_id,
                    trait=trait,
                    defaults={
                        'expected_date': expected_date,
                        'status_flag': flag,
                        'entered_by': None  # Can customize if needed
                    }
                )

        self.stdout.write(self.style.SUCCESS("Trait reminders updated successfully."))
