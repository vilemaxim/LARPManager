from django.contrib import admin
from .models import Event, Location, EventRegistration

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address')
    search_fields = ('name',)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'location', 'starting_character_points', 'attending_build', 'traveling_attending_build', 'max_monster_cores', 'is_active')
    list_filter = ('is_active', 'start_date', 'location')
    search_fields = ('name', 'description', 'location__name')

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at', 'has_paid')
    list_filter = ('has_paid', 'registered_at')
    search_fields = ('user__username', 'event__name')
