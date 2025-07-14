from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '-')

@register.filter
def status_class(value):
    return {
        "✔️": "bg-success text-white",
        "❌": "bg-danger text-white",
        "⏳": "bg-warning text-dark",
        "🕓": "bg-secondary text-white"
    }.get(value, "bg-light text-dark")
