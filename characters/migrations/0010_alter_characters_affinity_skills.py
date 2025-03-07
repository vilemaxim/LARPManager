# Generated by Django 4.2.9 on 2025-02-23 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cultivator_rules', '0001_initial'),
        ('characters', '0009_characterhistory_affinities_characters_affinities_and_more'),
    ]

    operations = [
        # Add the new field directly without trying to remove the old one
        migrations.AddField(
            model_name='characters',
            name='affinity_skills',
            field=models.ManyToManyField(
                blank=True,
                related_name='characters_with_affinity',
                through='characters.CharacterAffinitySkill',
                to='cultivator_rules.affinityskill'
            ),
        ),
    ]
