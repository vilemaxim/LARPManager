from django.db import models

class Affinity(models.Model):
    name = models.CharField(max_length=100, unique=True)
    cost_multiplier = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = "Affinity"
        verbose_name_plural = "Affinities"

    def __str__(self):
        return f"{self.name}"

class AffinitySkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    affinity = models.ForeignKey('Affinity', on_delete=models.CASCADE, related_name='skills')
    frequency = models.ForeignKey('Frequency', on_delete=models.SET_NULL, null=True, blank=True)
    build = models.PositiveIntegerField()
    prereqs = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='required_for')
    verbal = models.TextField(blank=True, null=True)
    description = models.TextField()
    delivery_method = models.ForeignKey('DeliveryMethod', on_delete=models.SET_NULL, null=True, blank=True)
    max_time_can_buy = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} ({self.affinity.name})"

class Race(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    costume_requirements = models.TextField()
    special_notes = models.TextField(blank=True)
    starting_affinity = models.ForeignKey('Affinity', on_delete=models.CASCADE, related_name="starting_races")
    starting_affinity_tier = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class RaceSkill(models.Model):
    race = models.ForeignKey('Race', on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)
    build = models.PositiveIntegerField()
    frequency = models.ForeignKey('Frequency', on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.ForeignKey('Duration', on_delete=models.SET_NULL, null=True, blank=True)
    verbal = models.TextField(blank=True, null=True)
    description = models.TextField()
    delivery_method = models.ForeignKey('DeliveryMethod', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.race.name})"

class CultivatorTier(models.Model):
    name = models.CharField(max_length=100, unique=True)
    build_low = models.PositiveIntegerField()
    build_high = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name}"

class Frequency(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Duration(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class DeliveryMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class CommonSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    frequency = models.ForeignKey('Frequency', on_delete=models.SET_NULL, null=True, blank=True)
    build = models.PositiveIntegerField()
    prereqs = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='required_for')
    description = models.TextField()
    duration = models.ForeignKey('Duration', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class StatusEffect(models.Model):
    TYPE_CHOICES = [
        ('physical', 'Physical'),
        ('mental', 'Mental'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Essence(models.Model):
    cost_per_point = models.PositiveIntegerField(default=1)
    max_extra_essence_per_tier = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Essence: Max Extra: {self.max_extra_essence_per_tier}, Cost per Point: {self.cost_per_point}"

