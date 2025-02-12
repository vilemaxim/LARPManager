from django.db import models
from django.contrib.auth.models import User
from events.models import Event
from cultivator_rules.models import Affinity, Race, RaceSkill, CultivatorTier, AffinitySkill, CommonSkill

class Characters(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="characters")
    name = models.CharField(max_length=200)
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name="characters")  
    cultivator_tier = models.ForeignKey(CultivatorTier, on_delete=models.SET_NULL, null=True, blank=True)  
    starting_build = models.PositiveIntegerField()
    total_build = models.PositiveIntegerField()
    unspent_build = models.PositiveIntegerField()
    unspent_affinity = models.PositiveIntegerField()
    armor = models.PositiveIntegerField(default=0)
    starting_event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name="starting_characters")  
    character_number = models.PositiveIntegerField(unique=True, null=True, blank=True)

    common_skills = models.ManyToManyField(CommonSkill, blank=True, related_name='characters_with_common')
    race_skills = models.ManyToManyField(RaceSkill, blank=True, related_name='characters_with_race')
    affinity_skills = models.ManyToManyField(AffinitySkill, blank=True, related_name='characters_with_affinity')
    affinities = models.ManyToManyField(Affinity, through='CharactersAffinities', related_name="characters_with_affinity")
    # Marshal Area
    approval_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_characters")
    approval_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending"
    )
    rejection_note = models.TextField(blank=True, null=True)
   
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    def save_snapshot(self, event):
        """Create a historical snapshot of the character at an event."""
        CharacterHistory.objects.create(
            character=self,
            event=event,
            name=self.name,
            race=self.race,
            cultivator_tier=self.cultivator_tier,
            starting_build=self.starting_build,
            total_build=self.total_build,
            unspent_build=self.unspent_build,
            unspent_affinity=self.unspent_affinity,
            armor=self.armor,
            essence=self.essence,
            common_skills=self.common_skills,
            race_skills=self.race_skills,
            affinity_skills=self.affinity_skills,
            affinities=self.affinities,
        )  

class CharacterHistory(models.Model):
    character = models.ForeignKey(Characters, on_delete=models.CASCADE, related_name="history")
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)  # When the snapshot was taken
    
    # Fields to store the character's state
    name = models.CharField(max_length=255)
    race = models.ForeignKey(Race, on_delete=models.SET_NULL, null=True)
    cultivator_tier = models.ForeignKey(CultivatorTier, on_delete=models.SET_NULL, null=True, blank=True)  
    starting_build = models.PositiveIntegerField()
    total_build = models.PositiveIntegerField()
    unspent_build = models.PositiveIntegerField()
    unspent_affinity = models.PositiveIntegerField()
    armor = models.PositiveIntegerField()
    essence = models.PositiveIntegerField()
    common_skills = models.ManyToManyField(CommonSkill, blank=True, related_name='characters_with_common_history')
    race_skills = models.ManyToManyField(RaceSkill, blank=True, related_name='characters_with_race_history')
    affinity_skills = models.ManyToManyField(AffinitySkill, blank=True, related_name='characters_with_affinity_history')
    affinities = models.ManyToManyField(Affinity, through='CharactersAffinities', related_name="characters_with_affinity_history")
    
    def __str__(self):
        return f"{self.character.name} - {self.event.name} Snapshot ({self.timestamp})"

class CharactersAffinities(models.Model):
    character = models.ForeignKey('Characters', on_delete=models.CASCADE, related_name="affinity_levels", null=True, blank=True)
    character_history = models.ForeignKey('CharacterHistory', on_delete=models.CASCADE, related_name="affinity_levels", null=True, blank=True)
    affinity = models.ForeignKey(Affinity, on_delete=models.CASCADE, related_name="character_levels")  
    level = models.PositiveIntegerField(default=1)
    cultivator_tier = models.ForeignKey(CultivatorTier, on_delete=models.SET_NULL, null=True, blank=True)  

    def __str__(self):
        if self.character:
            return f"{self.character.name} - {self.affinity.name} (Level {self.level})"
        elif self.character_history:
            return f"History ({self.character_history.character.name}) - {self.affinity.name} (Level {self.level})"
        return "Unassociated Affinity Record"

class CharactersRacialSkills(models.Model):
    character = models.ForeignKey(
        Characters, on_delete=models.CASCADE, related_name='character_race_skills'
    )
    race_skill = models.ForeignKey(RaceSkill, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.character.name} - {self.racial_skill.name}"

class SlottedCores(models.Model):
    character = models.ForeignKey('Characters', on_delete=models.CASCADE, related_name="slotted_affinities")
    cultivator_tier = models.ForeignKey(CultivatorTier, on_delete=models.CASCADE)  
    slotted_affinity_total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.character.name} - {self.cultivator_tier.name}: {self.slotted_affinity_total}"

class ExtraEssences(models.Model):
    character = models.ForeignKey('Characters', on_delete=models.CASCADE, related_name="extra_essences")
    cultivator_tier = models.ForeignKey(CultivatorTier, on_delete=models.CASCADE)
    extra_essence = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.character.name} - {self.cultivator_tier.name}: {self.extra_essence} Extra Essence"

class CharacterCommonSkill(models.Model):
    character = models.ForeignKey(
        Characters, on_delete=models.CASCADE, related_name='character_common_skills'
    )
    common_skill = models.ForeignKey(CommonSkill, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.character.name} - {self.common_skill.name}"
    
class CharacterAffinitySkill(models.Model):
    character = models.ForeignKey(
        Characters, on_delete=models.CASCADE, related_name='character_affinity_skills'
    )
    affinity_skill = models.ForeignKey(AffinitySkill, on_delete=models.CASCADE)
    level = models.PositiveIntegerField(default=1)  # Tracks how many levels of the skill are purchased
    cultivator_tier = models.ForeignKey(CultivatorTier, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.character.name} - {self.affinity_skill.name} (Level {self.level})"


class MonsterCoreSpent(models.Model):
    character = models.ForeignKey(Characters, on_delete=models.CASCADE, related_name="upgrades")
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.PositiveIntegerField()
    teir = models.ForeignKey(CultivatorTier, on_delete=models.SET_NULL, null=True, blank=True)
    for_build = models.BooleanField(default=False)
    for_affinity = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.character.name} Upgrade at {self.event.name} on {self.timestamp}"
