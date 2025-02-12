from django.core.management.base import BaseCommand
from cultivator_rules.models import Race, RaceSkill, Frequency

# Racial skills extracted with proper frequency separation
RACE_SKILLS_DATA = [
    {
        "race": "Amalgams",
        "skills": [
            {
                "name": "Animalistic Combat",
                "build": 4,
                "frequency": "Passive",
                "description": "Grants the Amalgams the Florentine skill when using claws and allows them to use 1 weapon and 1 claw simultaneously."
            },
            {
                "name": "Sharp Claws",
                "build": 3,
                "frequency": "Daily",
                "description": "The Amalgams can spend a minute of roleplay to sharpen their claws, resulting in their next attack doing double damage."
            },
            {
                "name": "Feral Dodge",
                "build": 4,
                "frequency": "Daily",
                "description": "The Amalgams may use the Dodge ability."
            },
            {
                "name": "Giant Leap",
                "build": 2,
                "frequency": "Daily",
                "description": "This skill allows the Amalgams to ignore one physical wall or obstacle."
            },
        ]
    },
    {
        "race": "Celestial",
        "skills": [
            {
                "name": "Protector of Life",
                "build": 2,
                "frequency": "Bell",
                "description": "The Celestial can use the Intercede skill."
            },
            {
                "name": "Lay on Hands",
                "build": 3,
                "frequency": "Weekend",
                "description": "The Celestial may heal a target for their Life affinity times 2, instantly."
            },
            {
                "name": "Rot Resistance",
                "build": 4,
                "frequency": "Weekend",
                "description": "The Celestial may resist 1 Death affinity ability."
            },
            {
                "name": "Portent of the Stars",
                "build": 4,
                "frequency": "Weekend",
                "description": "The Celestial can grant a target of their choice the Dodge skill."
            },
        ]
    },
    {
        "race": "Deadborn",
        "skills": [
            {
                "name": "No Pain",
                "build": 3,
                "frequency": "Weekend",
                "description": "The Deadborn may fight to negative 10 hitpoints. The Deadborn collapses at 0 at the end of the combat, or when they reach -10, whichever occurs first."
            },
            {
                "name": "No Metabolism",
                "build": 2,
                "frequency": "Passive",
                "description": "The Deadborn does not need to breathe or eat, making them immune to drowning or choking."
            },
            {
                "name": "The Dead Don't Bleed",
                "build": 4,
                "frequency": "Weekend",
                "description": "Resist 1 bleed, 1 disease, or 1 poison description."
            },
            {
                "name": "Make Whole",
                "build": 3,
                "frequency": "Weekend",
                "description": "The Deadborn may restore 1 lost limb with 1 minute of out-of-combat roleplay by harvesting a fallen ally or enemy's limb."
            },
        ]
    },
        {
        "race": "Drakeling",
        "skills": [
            {
                "name": "Water Jet",
                "build": 3,
                "frequency": "Daily",
                "description": "This ability will confer the Knockback description to the target."
            },
            {
                "name": "Freedom of Movement",
                "build": 1,
                "frequency": "Passive",
                "description": "The Drakeling is comfortable in water and suffers no slowed movement while submerged."
            },
            {
                "name": "Blind Fighting",
                "build": 2,
                "frequency": "Weekend",
                "description": "The Drakeling gains Blind Fighting for 30 minutes."
            },
            {
                "name": "Animalistic Combat",
                "build": 4,
                "frequency": "Passive",
                "description": "This grants the Drakeling the Florentine skill when using claws and allows them to use 1 weapon and 1 claw simultaneously."
            },
        ]
    },
    {
        "race": "Dryad/Arborkin",
        "skills": [
            {
                "name": "Entangle",
                "build": 4,
                "frequency": "Daily",
                "description": "This ability will confer the Entangle description to the target. Cast by Gesture."
            },
            {
                "name": "Regenerate Limb",
                "build": 2,
                "frequency": "Weekend",
                "description": "The Dryad can regrow a lost limb. This regrowth takes 1 chime to complete."
            },
            {
                "name": "Blooming Presence",
                "build": 3,
                "frequency": "Weekend",
                "description": "Auracast heal over time, healing allies equal to Wood Affinity per chime for Wood Affinity chimes."
            },
            {
                "name": "Entangling Roots",
                "build": 3,
                "frequency": "Daily",
                "description": "The Dryad plants their feet, allowing them to resist a movement description. While entangled, they heal hitpoints equal to their Wood affinity per chime."
            },
        ]
    },
    {
        "race": "Efreet",
        "skills": [
            {
                "name": "Portent of the Stars",
                "build": 4,
                "frequency": "Weekend",
                "description": "The Efreet can grant a target of their choice the Dodge skill."
            },
            {
                "name": "Heat of the Desert",
                "build": 3,
                "frequency": "Daily",
                "description": "The Efreet can cast Return Your Damage against an attack that successfully strikes them."
            },
            {
                "name": "Wandering Steps",
                "build": 2,
                "frequency": "Weekend",
                "description": "The Efreet may resist a Root description."
            },
            {
                "name": "Paths of Fate",
                "build": 2,
                "frequency": "Weekend",
                "description": "The Efreet may refresh 1 per-Bell skill after 1 minute of out-of-combat roleplay."
            },
        ]
    },
    {
        "race": "Half-Giant",
        "skills": [
            {
                "name": "Harden",
                "build": 4,
                "frequency": "Daily",
                "description": "The Half-Giant may use the Mitigate skill, reducing any one incoming attack from their tier or lower to 1."
            },
            {
                "name": "Strong Frame",
                "build": 2,
                "frequency": "Passive",
                "description": "Allows the Half-Giant to use their damage reduction on all attacks (melee, range, and magical) for 1 minute."
            },
            {
                "name": "Stone Armaments",
                "build": 2,
                "frequency": "Weekend",
                "description": "The Half-Giant can create a weapon and a shield for 30 minutes per Earth Affinity tier."
            },
            {
                "name": "Blood of the Earth",
                "build": 4,
                "frequency": "Weekend",
                "description": "Resist 1 bleed, 1 disease, or 1 poison description."
            },
        ]
    },
    {
        "race": "Imp",
        "skills": [
            {
                "name": "Incite Rage",
                "build": 3,
                "frequency": "Weekend",
                "description": "This ability will confer the Frenzy description to the target. Cast via Packet."
            },
            {
                "name": "Fire Resistance",
                "build": 3,
                "frequency": "Daily",
                "description": "Resist any fire attack/description of your tier or lower."
            },
            {
                "name": "Flame Weapon",
                "build": 3,
                "frequency": "Weekend",
                "description": "Coat your personal weapon in flames and transform the damage type to fire for 1 chime per Fire affinity tier."
            },
            {
                "name": "Heat of the Desert",
                "build": 3,
                "frequency": "Daily",
                "description": "The Imp can cast Lesser Damage Shield (Fire Affinity tier x3) against an attack that successfully strikes the Imp."
            },
        ]
    },
    {
        "race": "Kijin/Ork",
        "skills": [
            {
                "name": "Slam",
                "build": 4,
                "frequency": "Daily",
                "description": "Knocks the target back 3 steps and stuns them for 5 seconds. The movement description ends if the target comes into contact with another person or physical obstruction."
            },
            {
                "name": "Cleanse Your Mind",
                "build": 3,
                "frequency": "Daily",
                "description": "Grants 1 use of Cleanse Your Mind."
            },
            {
                "name": "Hard Headed",
                "build": 4,
                "frequency": "Weekend",
                "description": "Resist 1 Waylay."
            },
            {
                "name": "Fearful Shout",
                "build": 3,
                "frequency": "Weekend",
                "description": "This ability will confer the Frenzy description to the target. Cast via Aura."
            },
        ]
    },
    {
        "race": "Kitsune",
        "skills": [
            {
                "name": "Fox-like Charm",
                "build": 3,
                "frequency": "Bell",
                "description": "Charm one target creature, denoted by touch or packet delivery. This spell breaks if the caster attacks the target. Lasts 1 minute per Shadow Affinity."
            },
            {
                "name": "Animalistic Combat",
                "build": 4,
                "frequency": "Passive",
                "description": "Grants the Kitsune the Florentine skill when using claws and allows them to use 1 weapon and 1 claw simultaneously."
            },
            {
                "name": "Meld with Shadow",
                "build": 3,
                "frequency": "Daily",
                "description": "Meld with a shadow larger than themselves for a number of chimes equal to their Shadow Affinity. This counts as a Sanctuary description."
            },
            {
                "name": "Lick Wounds",
                "build": 2,
                "frequency": "Daily",
                "description": "Heals the Kitsune for their Shadow affinity every chime until fully healed. Cannot restore lost limbs or be used in combat."
            },
        ]
    },
    {
        "race": "Quicksilver",
        "skills": [
            {
                "name": "Shiny Body",
                "build": 3,
                "frequency": "Weekend",
                "description": "This ability will confer the Blind description to the target. Cast via Gesture."
            },
            {
                "name": "Sturdy",
                "build": 3,
                "frequency": "Weekend",
                "description": "Resist 1 Movement description."
            },
            {
                "name": "No Pain",
                "build": 3,
                "frequency": "Weekend",
                "description": "Fight to negative 10 hitpoints. Collapse at 0 at the end of combat or when reaching -10."
            },
            {
                "name": "Regenerate Limb",
                "build": 2,
                "frequency": "Weekend",
                "description": "Regrow a lost limb. This regrowth takes 1 chime to complete."
            },
        ]
    },
    {
        "race": "Veilkin",
        "skills": [
            {
                "name": "Illusionary Race",
                "build": 1,
                "frequency": "Passive",
                "description": "The Veilkin can purchase 1 racial from any other race. This becomes the Veilkin's illusionary race."
            },
            {
                "name": "Charm",
                "build": 2,
                "frequency": "Weekend",
                "description": "This ability will confer the Charm description to the target."
            },
            {
                "name": "Light Construct",
                "build": 4,
                "frequency": "Weekend",
                "description": "The Veilkin gains a single use of the Dodge skill."
            },
            {
                "name": "Cleansing Light",
                "build": 3,
                "frequency": "Daily",
                "description": "The Veilkin can remove one negative status description from themselves or an ally."
            },
        ]
    }
]

class Command(BaseCommand):
    help = "Imports racial skills into the database"

    def handle(self, *args, **kwargs):
        for race_data in RACE_SKILLS_DATA:
            race_name = race_data["race"]
    
            try:
                race = Race.objects.get(name=race_name)
            except Race.DoesNotExist:
                print(f"❌ ERROR: Race '{race_name}' does not exist in the database!")
                race = None

            if race: 
                for skill in race_data["skills"]:
                    frequency = Frequency.objects.get(name=skill["frequency"])
                    race_skill, created = RaceSkill.objects.update_or_create(
                        race=race,
                        name=skill["name"],
                        defaults={
                            "build": skill["build"],
                            "frequency": frequency,
                            "description": skill["description"]
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"✅ Created skill: {skill['name']} for {race_name}"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"🔄 Updated skill: {skill['name']} for {race_name}"))
