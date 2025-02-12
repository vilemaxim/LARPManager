from django.core.management.base import BaseCommand
from cultivator_rules.models import Race, Affinity

RACE_AFFINITIES = {
    "Amalgam": "Attack",
    "Celestial": "Life",
    "Deadborn": "Death",
    "Drakeling": "Water",
    "Dryad/Arborkin": "Wood",
    "Efreet": "Fate",
    "Half-Giant": "Earth",
    "Imp": "Fire",
    "Kijin/Ork": "Body",
    "Kitsune": "Shadow",
    "Quicksilver": "Metal",
    "Veilkin": "Light",
}

HUMAN_AFFINITIES = ["Fire", "Water", "Earth", "Metal", "Wood"]

RACE_DESCRIPTIONS = {
    "Amalgam": "Human-like beast folk with animal-like features...",
    "Celestial": "Champions from the plane of Life, dedicated to fighting Outsiders...",
    "Deadborn": "Reanimated corpses, spirits inhabiting recently deceased bodies...",
    "Drakeling": "Descendants of ancient Sovereign dragons, possessing reptilian traits...",
    "Dryad/Arborkin": "Plant-like beings with bark-like skin and a deep connection to nature...",
    "Efreet": "Fiery beings known for their resistance to heat and trickster nature...",
    "Half-Giant": "Gentle yet intimidating beings with a strong bond to nature...",
    "Human": "Humans of the Crucible come in all shapes and sizes. The most numerous and adaptable of the humanoids, many of those found in the world are human. The cultures of man are many, but our region has 4 major subsets.",
    "Imp": "Mischievous beings born of fire, often distrusted by the superstitious...",
    "Kijin/Ork": "Powerful humanoids focused on body cultivation and living in clans...",
    "Kitsune": "Fox-like humanoids descended from ancient beings of shadow...",
    "Quicksilver": "Artificial constructs with spirits and metallic appearance...",
    "Veilkin": "Natural illusionists and infiltrators with an unknown true form...",
}

COSTUME_REQUIREMENTS = {
    "Amalgam": "Amalgam must wear face paint, a mask, or other accessories to physically represent their animal component. Each animal will be approved on a case-by-case basis. Foxes are not permitted for Amalgam; please see Kitsune.",
    "Celestial": "Ear tips and a gold sigil, wings optional.",
    "Deadborn": "Eyes should be completely surrounded by dark makeup of black or purple. The “eye circle” can be of any actual shape or design. Because Deadborn are very zombielike in appearance, players must add in exposed bones or bits of decaying flesh to complete their personal look. Deadborn can be the corpse of other PC races. However, due to the nature of death, any races with claws are reborn with their claws non-functional and they may not be used.",
    "Drakeling": "Reptilian prosthetics, wings optional.",
    "Dryad/Arborkin": "Players will use branches, vines, and other foliage through their costuming and/or hair to clearly denote their race. Optional bark.",
    "Efreet": "Efreet have red or yellow tattoos and sigils on their face, and may have small horn nubs (optional).",
    "Half-Giant": "Grey tinged skin look like they are made of stone, optional cracks and fissures.",
    "Human": "See rules p41",
    "Imp": "Red makeup with black sigil/s.",
    "Kijin/Ork": "Green tinged skin, pronounced lower tusks. Jaw or Brow prosthetic optional.",
    "Kitsune": "Kitsune must wear Fox ears and at least 1 tail. Additional tails as appropriate for the storyline are optional.",
    "Quicksilver": "Metallic eye makeup or sigil.",
    "Veilkin": "A white or pale blue sigil on face; raised brow optional.",
}


SPECIAL_NOTES = {
    "Amalgam": "Amalgam start at Attack Affinity, Tier 1.The character can use two 24 inch claw reps. Claws treat a Break Weapon effect as a Break Limb effect instead (The call for this is, “got it, claws, reduced.”). Claws are immune to Disarm. Claws cannot have poisons applied to them or become enchanted unless another skill allows it. Claw reps must be built as standard short swords, red in color.",
    "Celestial": "Celestials gains Life Affinity, Tier 1.",
    "Deadborn": "As Deadborn have previously experienced the throes of death, Deadborn gain the Death Affinity, Tier 1 for free.",
    "Drakeling": "Drakelings gain Water Affinity, Tier 1. The character can use two 24 inch claw reps. Claws treat a Break Weapon effect as a Break Limb effect instead (the call for this is, “got it, claws, reduced.”). Claws are immune to Disarm. Claws cannot have poisons applied to them or become enchanted unless another skill allows it. Claw reps must be built as standard short swords, red in color.",
    "Dryad/Arborkin": "Dryads gain Wood Affinity, Tier 1.",
    "Efreet": "Due to their mystic nature, Efreet gain Fate Affinity, Tier 1.",
    "Half-Giant": "Half-giants gain Earth Affinity, Tier 1.",
    "Human": "Humans start with Affinity, Tier 1 in any one of the base 5 elements (Wood, Fire, Earth, Metal, Water).",
    "Imp": "Weak to Purification magic. Cannot take Life Affinity.",
    "Kijin/Ork": "Tribal structure; gains benefits from warbands.",
    "Kitsune": "Can shift forms between fox and humanoid form at will (roleplay-only).",
    "Quicksilver": "Takes extra damage from Rust and Metal-based abilities.",
    "Veilkin": "Naturally adept in stealth and illusion magic.",
}

class Command(BaseCommand):
    help = "Import races and their free racial affinities into the database"

    def handle(self, *args, **kwargs):
        for race_name, affinity_name in RACE_AFFINITIES.items():
            affinity = Affinity.objects.filter(name=affinity_name).first()
            if not affinity:
                self.stdout.write(self.style.ERROR(f"Affinity '{affinity_name}' not found. Skipping {race_name}."))
                continue

            race, created = Race.objects.get_or_create(
                name=race_name,
                defaults={
                    "starting_affinity": affinity,
                    "starting_affinity_tier": 1,
                    "description": RACE_DESCRIPTIONS.get(race_name, "No description available."),
                    "costume_requirements": COSTUME_REQUIREMENTS.get(race_name, "No specific costume requirement."),
                    "special_notes": SPECIAL_NOTES.get(race_name, "No special racial restrictions.")
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added race: {race.name} with affinity {affinity.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Race already exists: {race.name}"))

        # Handle Humans separately
        for affinity_name in HUMAN_AFFINITIES:
            affinity = Affinity.objects.filter(name=affinity_name).first()
            if not affinity:
                self.stdout.write(self.style.ERROR(f"Affinity '{affinity_name}' not found for Humans. Skipping Human-{affinity_name}."))
                continue

            race_name = f"Human - {affinity_name}"
            race, created = Race.objects.get_or_create(
                name=race_name,
                defaults={
                    "starting_affinity": affinity,
                    "starting_affinity_tier": 1,
                    "description": "Humans can select from any elemental affinity.",
                    "costume_requirements": "No specific costume requirement.",
                    "special_notes": "No special racial restrictions."
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully added race: {race.name} with affinity {affinity.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Race already exists: {race.name}"))

