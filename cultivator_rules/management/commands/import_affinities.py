from django.core.management.base import BaseCommand
from cultivator_rules.models import Affinity

AFFINITIES = [
    ("Earth", 1),
    ("Metal", 1),
    ("Water", 1),
    ("Wood", 1),
    ("Fire", 1),
    ("Death", 2),
    ("Life", 2),
    ("Light", 2),
    ("Shadow", 2),
    ("Fate", 2),
    ("Attack", 2),
    ("Body", 2),
]

class Command(BaseCommand):
    help = "Imports predefined affinities into the database"

    def handle(self, *args, **kwargs):
        for name, cost_multiplier in AFFINITIES:
            affinity, created = Affinity.objects.get_or_create(
                name=name,
                defaults={'cost_multiplier': cost_multiplier}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✅ Added affinity: {name} (Cost Multiplier: {cost_multiplier})'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠️ Affinity already exists: {name}'))

        self.stdout.write(self.style.SUCCESS("✅ Affinity import completed!"))
