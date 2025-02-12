from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name', 'description', 'start_date', 'end_date', 'location',
            'starting_character_points', 'is_active', 'attending_build',
            'traveling_attending_build', 'max_monster_cores'
        ]
