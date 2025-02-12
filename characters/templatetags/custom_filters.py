from django import template
from events.models import Event

register = template.Library()

@register.filter
def get_event_points(event_id):
    try:
        event = Event.objects.get(id=event_id)
        return event.starting_character_points
    except Event.DoesNotExist:
        return 0

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, None)