from django.core.management.base import BaseCommand
from cultivator_rules.models import Affinity, AffinitySkill, Frequency, Duration, DeliveryMethod

EARTH_SKILLS = [
    {
        "name": "Mote of Earth",
        "frequency": "At Will",
        "build_cost": [4],
        "prerequisites": [],
        "verbal": "By Earth, Mote of Earth: (Damage).",
        "description": "Deals 1 damage. At Affinity 3 and Affinity 6, the damage increases by one. This ability has a 5-second cooldown.",
        "delivery_method": "Packet",
    },
    {
        "name": "Wall of Earth",
        "frequency": "Encounter",
        "build_cost": [5, 4, 3, 2],
        "prerequisites": [],
        "verbal": "By Earth, I summon a wall.",
        "description": "Summons an impassible wall that lasts for 1 minute. Walls created out of combat last for 1x Earth affinity hours. Walls require a status card with times and can be refreshed. The wall is 10ftx10ft and has 10 Structural Points of health.",
        "delivery_method": "Touch",
    },
    {
        "name": "Taunt",
        "frequency": "Encounter",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "By Earth, Fight me (Taunt).",
        "description": "This ability confers the Taunt effect to the target.",
        "delivery_method": "Aura",
    },
    {
        "name": "Deflect",
        "frequency": "Encounter",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "(Deflect)",
        "description": "Prevents a physical ranged attack from dealing damage to you. Does not work against surprise or AOE attacks.",
        "delivery_method": "",
    },
    {
        "name": "Intercede",
        "frequency": "Encounter",
        "build_cost": [5, 4, 3, 2],
        "prerequisites": [],
        "verbal": "(Intercede)",
        "description": "Allows you to put yourself between an attack and a target within weapon’s reach, taking the damage/healing and/or effect in the target’s place.",
        "delivery_method": "",
    },
    {
        "name": "Knockback",
        "frequency": "Encounter",
        "build_cost": [2, 1, 1, 1],
        "prerequisites": [],
        "verbal": "(Knockback)",
        "description": "This ability confers the Knockback effect to the target.",
        "delivery_method": "Weapon",
    },
    {
        "name": "Unmovable Stone",
        "frequency": "Encounter",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "(Resist)",
        "description": "Allows you to Resist a single movement effect.",
        "delivery_method": "",
    },
    {
        "name": "Stun",
        "frequency": "Encounter",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "(Stun)",
        "description": "This ability confers the Stun effect to the target.",
        "delivery_method": "Weapon",
    },
    {
        "name": "Stoneblood",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "By Earth, I grant you stoneblood (Number).",
        "description": "Grants 1x your tier-adjusted Earth affinity temporary health to the target. This health lasts for one hour or until used.",
        "delivery_method": "Touch",
    },
    {
        "name": "Stoneskin",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": ["Stoneblood"],
        "verbal": "By Earth, I grant you stoneskin.",
        "description": "Grants the target DR 1 for 1 minute.",
        "delivery_method": "Touch",
    },
    {
        "name": "Pocket Sand",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "By Earth, I blind you.",
        "description": "Confers the Blind effect to the target.",
        "delivery_method": "Packet",
    },
    {
        "name": "Break Limb",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "(Break Limb)",
        "description": "Confers the Break Limb effect to the target.",
        "delivery_method": "Weapon",
    },
    {
        "name": "Stone Shield",
        "frequency": "Bell",
        "build_cost": [5, 4, 3, 2],
        "prerequisites": [],
        "verbal": "By the immovable earth, I summon a stone shield.",
        "description": "Summons a usable shield made of stone for 1x your tier-adjusted Earth affinity.",
        "delivery_method": "",
    },
    {
        "name": "Trip",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "By Earth, I trip you.",
        "description": "Confers the Trip effect to the target.",
        "delivery_method": "Packet",
    },
    {
        "name": "Mitigate",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "(Mitigate)",
        "description": "Reduces the damage of a single incoming attack to 1. The attack must be of the same tier or lower. Does not work against surprise or AOE attacks.",
        "delivery_method": "",
    },
    {
        "name": "Obscuring Sands",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": [],
        "verbal": "By Earth, I cast obscuring sands.",
        "description": "For one minute, the target cannot make any attacks from outside of melee range and is protected from all attacks outside of melee range.",
        "delivery_method": "Packet",
    },
    {
        "name": "Blinding Sands",
        "frequency": "Daily",
        "build_cost": [6, 5, 4, 3],
        "prerequisites": ["Pocket Sand"],
        "verbal": "By the swirling sands, I blind you all. Sweeping Blindness.",
        "description": "Confers the Blind effect to everyone, allies included, within close range.",
        "delivery_method": "Aura",
    },
    {
        "name": "Total Defense",
        "frequency": "Weekend",
        "build_cost": [7, 6],
        "prerequisites": ["Taunt", "Earthen Shell", "Affinity 3/6"],
        "verbal": "By the swirling sands and immovable earth, Fight Me (Taunt, 1 minute). (Weapon Strike - Mitigate) (All status effects - Resist).",
        "description": "Taunts the target for 1 minute, forcing them to attack you. Each weapon strike is mitigated, and all status effects are ignored for 1 minute per tier-adjusted Earth affinity. After using, you must roleplay extreme fatigue for 1 minute.",
        "delivery_method": "Aura",
    },
    {
        "name": "Lesser Resist Water",
        "frequency": "Bell",
        "build_cost": [4, 3, 2, 1],
        "prerequisites": None,
        "verbal": "By Earth, I grant you a resistance to Water.",
        "description": "Stops the next Water spell, harmful or beneficial, that is not self-cast. This skill lasts until invoked. Automatic effect.",
        "delivery_method": "Touch",
    },
]


class Command(BaseCommand):
    help = "Imports Earth Skills into the database"

    def handle(self, *args, **kwargs):
        earth_affinity, _ = Affinity.objects.get_or_create(name="Earth")

        for skill_data in EARTH_SKILLS:
            frequency = Frequency.objects.get(name=skill_data["frequency"])
            if skill_data["delivery_method"]:
                delivery_method = DeliveryMethod.objects.get(name=skill_data["delivery_method"])
            else:
                delivery_method = None

           
            skill, created = AffinitySkill.objects.get_or_create(
                name=skill_data["name"],
                affinity=earth_affinity,
                frequency=frequency,
                delivery_method=delivery_method,
                defaults={
                    "build": skill_data["build_cost"][0],
                    "verbal": skill_data["verbal"],
                    "description": skill_data["description"],
                },
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added Earth Skill: {skill.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Earth Skill already exists: {skill.name}"))

        self.stdout.write(self.style.SUCCESS("Earth Skills Import Completed!"))
