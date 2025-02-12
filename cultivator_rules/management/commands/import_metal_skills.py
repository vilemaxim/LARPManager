from django.core.management.base import BaseCommand
from cultivator_rules.models import Affinity, AffinitySkill, Frequency, Duration, DeliveryMethod

METAL_SKILLS = [
    {
        "name": "Mote of Metal",
        "frequency": "At Will",
        "build_cost": [4],
        "prereqs": None,
        "verbals": "By Metal, Mote of Metal: (Damage)",
        "description": "Deals 1 damage. At Affinity 3 and Affinity 6, the damage increases by one. This ability has a 5-second cooldown.",
        "delivery_method": "Packet"
    },
    {
        "name": "Backlash of the Blade",
        "frequency": "Encounter",
        "build_cost": [5, 4, 3, 2],
        "prereqs": None,
        "verbals": "By Metal, I grant you a backlash of the blade. (On invoke) Backlash: (Damage).",
        "description": "When a physical attack strikes you, you may call Backlash damage to the target equal to 1x your tier-adjusted Metal affinity in response. You still take the effects of the attack which triggered this ability. You may only have a single Backlash skill active at a time. This ability remains active for a number of hours equal to your Metal affinity or until invoked.",
        "delivery_method": "Gesture"
    },
    {
        "name": "Needle",
        "frequency": "Encounter",
        "build_cost": [6, 5, 4, 3],
        "prereqs": None,
        "verbals": "By Metal, I cast needle (damage).",
        "description": "You deal 1x your tier-adjusted Metal affinity damage to the target instantly.",
        "delivery_method": "Packet"
    },
    {
        "name": "Stun (Metal)",
        "frequency": "Encounter",
        "build_cost": [4, 3, 2, 1],
        "prereqs": None,
        "verbals": "(Stun)",
        "description": "This ability will confer the Stun effect to the target.",
        "delivery_method": "Weapon"
    },
    {
        "name": "Bypass Armor",
        "frequency": "Encounter",
        "build_cost": [5, 4, 3, 2],
        "prereqs": None,
        "verbals": "(Bypass Armor)",
        "description": "This skill bypasses the target's armor and deals full damage regardless of whether the area is covered or not.",
        "delivery_method": "Weapon"
    },
    {
        "name": "Sharpen",
        "frequency": "Bell",
        "build_cost": [8, 7, 6, 5],
        "prereqs": None,
        "verbals": "By Metal, I sharpen my blade.",
        "description": "Increases the damage of your physical attacks by 1/2 per your tier-adjusted Metal affinity (rounded up) for 1 minute.",
        "delivery_method": "Touch"
    },
    {
        "name": "Blind",
        "frequency": "Bell",
        "build_cost": [6, 5, 4, 3],
        "prereqs": None,
        "verbals": "By Metal, I blind you. (Surefire Blindness)",
        "description": "This ability will confer the Blind effect to the target.",
        "delivery_method": "Gesture"
    },
    {
        "name": "After Image",
        "frequency": "Bell",
        "build_cost": [7, 6, 5, 4],
        "prereqs": "Surefire (copied attack)",
        "verbals": None,
        "description": "Allows you to instantly deal a duplicate weapon attack or weapon-delivered skill to the same target of your previous attack.",
        "delivery_method": "Surefire"
    },
    {
        "name": "Mitigate (Metal)",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prereqs": None,
        "verbals": "(Mitigate)",
        "description": "Allows you to reduce the damage of a single incoming attack to 1. The attack must be of the same tier as yourself or lower. This does not work against surprise or AOE attacks.",
        "delivery_method": None
    }
]

class Command(BaseCommand):
    help = "Imports Metal Skills into the database"

    def handle(self, *args, **kwargs):
        metal_affinity, _ = Affinity.objects.get_or_create(name="Metal")

        for skill_data in METAL_SKILLS:
            frequency = Frequency.objects.get(name=skill_data["frequency"])
            if skill_data["delivery_method"]:
                delivery_method = DeliveryMethod.objects.get(name=skill_data["delivery_method"])
            else:
                delivery_method = None

           
            skill, created = AffinitySkill.objects.get_or_create(
                name=skill_data["name"],
                affinity=metal_affinity,
                frequency=frequency,
                delivery_method=delivery_method,
                defaults={
                    "build": skill_data["build_cost"][0],
                    "verbal": skill_data["verbals"],
                    "description": skill_data["description"],
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added Metal Skill: {skill.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Metal Skill already exists: {skill.name}"))

        self.stdout.write(self.style.SUCCESS("Metal Skills Import Completed!"))
