# Generated by Django 4.2.9 on 2025-02-01 22:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characters',
            name='character_number',
            field=models.PositiveIntegerField(null=True, unique=True),
        ),
    ]
