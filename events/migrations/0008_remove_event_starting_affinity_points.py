# Generated by Django 4.2.9 on 2025-02-24 03:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_event_starting_affinity_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='starting_affinity_points',
        ),
    ]
