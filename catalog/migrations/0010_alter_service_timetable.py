# Generated by Django 5.0.6 on 2024-06-28 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0009_service_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='timetable',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
