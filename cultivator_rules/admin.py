from django.contrib import admin
from .models import Affinity, AffinitySkill, Race, RaceSkill, CultivatorTier, Frequency, Duration, DeliveryMethod, CommonSkill, StatusEffect, Essence

@admin.register(Affinity)
class AffinityAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost_multiplier')
    search_fields = ('name',)

@admin.register(AffinitySkill)
class AffinitySkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'affinity', 'build', 'max_time_can_buy')
    search_fields = ('name', 'description', 'affinity__name')

@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'starting_affinity', 'starting_affinity_tier')
    search_fields = ('name', 'description', 'starting_affinity__name')

@admin.register(RaceSkill)
class RaceSkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'race', 'build')
    search_fields = ('name', 'race__name')

@admin.register(CultivatorTier)
class CultivatorTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'build_low', 'build_high')
    search_fields = ('name',)
    
@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the name of the frequency
    search_fields = ('name',)  # Allow searching by name


@admin.register(Duration)
class DurationAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the name of the duration
    search_fields = ('name',)  # Allow searching by name


@admin.register(DeliveryMethod)
class DeliveryMethodAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display the name of the delivery method
    search_fields = ('name',)  # Allow searching by name


@admin.register(CommonSkill)
class CommonSkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'build', 'frequency', 'duration')  # Display relevant fields
    search_fields = ('name', 'description')  # Allow searching by name and description
    list_filter = ('frequency', 'duration')  # Add filters for frequency and duration

@admin.register(StatusEffect)
class StatusEffectAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'description')
    search_fields = ('name', 'description')
    list_filter = ('type',)

@admin.register(Essence)
class EssenceAdmin(admin.ModelAdmin):
    list_display = ('cost_per_point', 'max_extra_essence_per_tier')
    search_fields = ('cost_per_point', 'max_extra_essence_per_tier')
    list_filter = ('cost_per_point', 'max_extra_essence_per_tier')