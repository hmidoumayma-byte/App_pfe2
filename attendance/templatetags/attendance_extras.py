from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Récupère une valeur dans un dict par clé — utilisé dans les templates de planning."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []


@register.filter
def absence_percent(absences, total):
    """Calcule le pourcentage d'absences."""
    if not total:
        return 0
    return round((absences / total) * 100, 1)