from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def get_first_value_keys(d):
    """
    Extracts the first dictionary's keys from a nested dictionary.
    Used to infer trait names from the first plot.
    """
    return list(d.values())[0].keys() if d else []

@register.filter
def get_nested(d, key):
    """
    Safe way to access nested dictionaries in templates.
    For example: {{ trait_summary|get_nested:trait|get_item:"✔️" }}
    """
    return d.get(key, {}) if isinstance(d, dict) else {}

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
