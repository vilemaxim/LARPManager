from django.core.management.base import BaseCommand
from cultivator_rules.models import CommonSkill, Frequency, Duration

COMMON_SKILLS = [
    {"name": "Buckler", "frequency": "Passive", "build": 2, "prereqs": [], 
     "description": "Allows the use of a buckler with a max area of 255 sq inches or an 18\" diameter.", "duration": "Passive"},
    {"name": "Shield", "frequency": "Passive", "build": 3, "prereqs": ["Buckler"], 
     "description": "Allows the player to use a shield with a max diameter of 28\". Non-circular shields must conform to specific size constraints.", "duration": "Passive"},
    {"name": "Shield (Exotic)", "frequency": "Passive", "build": 4, "prereqs": ["Shield"], 
     "description": "Allows the use of any shields that do not conform to normal descriptions (e.g., dart shields, oversized shields).", "duration": "Passive"},
    {"name": "Florentine", "frequency": "Passive", "build": 4, "prereqs": [], 
     "description": "Allows you to wield a one-handed and short weapon in either hand for combat.", "duration": "Passive"},
    {"name": "Master Florentine", "frequency": "Passive", "build": 3, "prereqs": ["Florentine"], 
     "description": "Allows you to wield a one-handed weapon in each hand for combat.", "duration": "Passive"},
    {"name": "Grand Master Florentine", "frequency": "Passive", "build": 3, "prereqs": ["Master Florentine"], 
     "description": "Allows you to wield a two-handed and one-handed weapon in either hand for combat. The two-handed weapon will only deal one-handed weapon damage.", "duration": "Passive"},
    {"name": "Literacy", "frequency": "Passive", "build": 2, "prereqs": [], 
     "description": "Allows you to read and write. Required to read/write blueprints, spell scrolls, or scribe talismans.", "duration": "Passive"},
    {"name": "Identify", "frequency": "Passive", "build": 1, "prereqs": [], 
     "description": "Allows the user to determine the primary affinity of a monster or cultivator with 10 seconds of visual inspection. One-time use per bell. Can be obfuscated.", "duration": "Passive"},
    {"name": "Examination", "frequency": "Per Bell", "build": 2, "prereqs": ["Identify"], 
     "description": "Once per bell, you can get one characteristic from a fallen monster, such as hit points, affinity depth, special attacks, defenses, or potential reagents.", "duration": "Passive"},
    {"name": "Weapon Skill - 2H", "frequency": "Passive", "build": 2, "prereqs": [], 
     "description": "Allows the use of any two-handed LARP-safe and approved weapon in combat.", "duration": "Passive"},
    {"name": "Weapon Skill - Bows", "frequency": "Passive", "build": 2, "prereqs": [], 
     "description": "Allows the use of a Nerf bow as a combat weapon.", "duration": "Passive"},
    {"name": "Exotic Weapon Skill - Throwing", "frequency": "Passive", "build": 3, "prereqs": [], 
     "description": "Allows the use of throwing weapons as combat weapons.", "duration": "Passive"},
    {"name": "Exotic Weapon Skill - Other", "frequency": "Passive", "build": 4, "prereqs": [], 
     "description": "Allows the use of an approved LARP-safe weapon not covered under Rules of Arms. Requires Plot/Staff approval.", "duration": "Passive"},
    {"name": "Evaluate Item", "frequency": "Passive", "build": 5, "prereqs": [], 
     "description": "Grants insight into the value of an item in a merchant's possession.", "duration": "Passive"},
    {"name": "Lockpicking", "frequency": "Passive", "build": 4, "prereqs": [], 
     "description": "Allows you to pick a lock up to your highest affinity level.", "duration": "Passive"},
    {"name": "Harvest", "frequency": "Passive", "build": 3, "prereqs": ["Wood Affinity"], 
     "description": "Allows gathering of herbs up to 1+ your affinity level.", "duration": "Instant"},
    {"name": "Distill", "frequency": "Passive", "build": 3, "prereqs": ["Water Affinity"], 
     "description": "Allows you to take two lower-quality liquid reagents and distill them into a single higher-tier liquid, up to 1+ your affinity level.", "duration": "Instant"},
    {"name": "Destroy", "frequency": "Passive", "build": 3, "prereqs": ["Fire Affinity"], 
     "description": "Allows you to destroy items and recover a single crafting reagent used to produce the item, up to 1+ your affinity level.", "duration": "Instant"},
    {"name": "Refine", "frequency": "Passive", "build": 3, "prereqs": ["Metal Affinity"], 
     "description": "Turns two lower-class metal reagents into one higher-tier metal reagent, up to 1+ your affinity level.", "duration": "Instant"},
    {"name": "Mining", "frequency": "Passive", "build": 3, "prereqs": ["Earth Affinity"], 
     "description": "Allows you to gather minerals up to 1+ your affinity level.", "duration": "Instant"},
    {"name": "Crafter's Mentality", "frequency": "Passive", "build": 3, "prereqs": [], 
     "description": "Allows you to treat one reagent while crafting as one tier higher.", "duration": "Passive"},
    {"name": "Crafter's Focus", "frequency": "Passive", "build": 4, "prereqs": ["Crafter's Mentality"], 
     "description": "Allows you to treat one reagent while crafting as one tier higher. Stacks with Crafter’s Mentality.", "duration": "Passive"},
    {"name": "Light Armor", "frequency": "Passive", "build": 1, "prereqs": [], 
     "description": "Provides DR 1 over the entire covered area. You must wear Light Armor to gain DR benefits.", "duration": "Passive"},
    {"name": "Medium Armor", "frequency": "Passive", "build": 2, "prereqs": ["Light Armor"], 
     "description": "Provides DR 2 to all covered areas. Fair DR without restricting skill use.", "duration": "Passive"},
    {"name": "Heavy Armor", "frequency": "Passive", "build": 4, "prereqs": ["Medium Armor"], 
     "description": "Provides DR 3 to all covered areas. Wearing heavy armor prevents the use of Dodge or Evade skills unless Body 3 or 6 in the appropriate tier is met.", "duration": "Passive"},
    {"name": "Backstab", "frequency": "Passive", "build": 7, "prereqs": [], 
     "description": "One weapon attack to the back deals one additional damage. You must see both shoulder blades to use this.", "duration": "Passive"},
    {"name": "Uncanny Defense", "frequency": "Passive", "build": 4, "prereqs": [], 
     "description": "Allows for the use of a defense skill to avoid an AOE effect.", "duration": "Passive"},
    {"name": "Blind Fighting", "frequency": "Passive", "build": 5, "prereqs": [], 
     "description": "Allows you to fight normally while blinded or in complete darkness.", "duration": "Passive"},
]


class Command(BaseCommand):
    help = "Import Common Skills from extracted rulebook data."

    def handle(self, *args, **kwargs):
        for skill_data in COMMON_SKILLS:
            frequency, _ = Frequency.objects.get_or_create(name=skill_data["frequency"])
            duration, _ = Duration.objects.get_or_create(name=skill_data["duration"]) if skill_data["duration"] else (None, None)

            skill, created = CommonSkill.objects.get_or_create(
                name=skill_data["name"],
                defaults={
                    "frequency": frequency,
                    "build": skill_data["build"],
                    "description": skill_data["description"],
                    "duration": duration
                }
            )

            if skill_data["prereqs"]:
                prereq_skills = CommonSkill.objects.filter(name=skill_data["prereqs"])
                skill.prereqs.set(prereq_skills)

            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added common skill: {skill.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Common skill already exists: {skill.name}"))
