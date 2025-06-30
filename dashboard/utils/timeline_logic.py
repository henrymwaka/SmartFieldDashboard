
from datetime import datetime, timedelta

def compute_trait_status(planting_date, trait_schedule, today=None):
    if today is None:
        today = datetime.today()
    status_dict = {}
    for trait, offset_days in trait_schedule.items():
        expected_date = planting_date + timedelta(days=offset_days)
        delta = (today - expected_date).days
        if delta < -5:
            status = "🕓"  # Too early
        elif -5 <= delta <= 3:
            status = "⏳"  # Due soon
        elif delta > 3:
            status = "❌"  # Overdue
        else:
            status = "✔️"  # Ideal window
        status_dict[trait] = {
            "expected_date": expected_date.strftime('%Y-%m-%d'),
            "status": status
        }
    return status_dict
