from django.utils import timezone

def calculate_trait_reminder_status(expected_date, actual_date):
    """
    Determines the status of a trait reminder based on expected and actual dates.
    Returns one of the following:
    - "❌ Overdue": if no actual date and expected date is in the past
    - "⏳ Due Soon": if no actual date and expected date is today or in the future
    - "🕓 Too Early": if data was collected earlier than expected
    - "✔️ Completed": if data was collected on time or later
    """
    if actual_date is None:
        if expected_date and expected_date < timezone.now().date():
            return "❌ Overdue"
        return "⏳ Due Soon"
    
    if actual_date < expected_date:
        return "🕓 Too Early"
    
    return "✔️ Completed"
