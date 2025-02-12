from django import forms
from .models import Characters

class CharacterCreationForm(forms.ModelForm):
    class Meta:
        model = Characters
        fields = ['name', 'race', 'starting_event']  
        widgets = {
            'starting_event': forms.Select(attrs={'class': 'form-control', 'required': 'required'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter character name'}),
            'race': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Character Name',
            'race': 'Race',
            'starting_event': 'Starting Event',
        }
