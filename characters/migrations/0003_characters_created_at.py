# Generated by Django 4.2.9 on 2025-02-01 22:28

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0002_alter_characters_character_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='characters',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
