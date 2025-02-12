from django.contrib import admin
from .models import Characters, CharactersAffinities, CharactersRacialSkills, SlottedCores, ExtraEssences, CharacterAffinitySkill, CharacterCommonSkill

@admin.register(Characters)
class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'race', 'cultivator_tier', 'starting_build', 'unspent_build', 'starting_event')  
    search_fields = ('name', 'user__username', 'race__name', 'starting_event__name')
    list_filter = ('race', 'cultivator_tier', 'starting_event')

@admin.register(CharactersAffinities)
class CharacterAffinityAdmin(admin.ModelAdmin):
    list_display = ('character', 'affinity', 'level', 'cultivator_tier')
    search_fields = ('character__name', 'affinity__name')

@admin.register(CharactersRacialSkills)
class CharacterRacialSkillAdmin(admin.ModelAdmin):
    list_display = ('character', 'race_skill')
    search_fields = ('character__name', 'racial_skill__name')

@admin.register(SlottedCores)
class SlottedCoresAdmin(admin.ModelAdmin):
    list_display = ('character', 'cultivator_tier', 'slotted_affinity_total')

@admin.register(ExtraEssences)
class ExtraEssenceAdmin(admin.ModelAdmin):
    list_display = ('character', 'cultivator_tier', 'extra_essence')

@admin.register(CharacterAffinitySkill)
class CharacterAffinitySkillAdmin(admin.ModelAdmin):
    list_display = ('character', 'affinity_skill', 'level')
    search_fields = ('character__name', 'affinity_skill__name')

@admin.register(CharacterCommonSkill)
class CharacterCommonSkillAdmin(admin.ModelAdmin):
    list_display = ('character', 'common_skill')
    search_fields = ('character__name', 'common_skill__name')