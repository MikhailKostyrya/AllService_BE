# Generated by Django 5.0.6 on 2024-06-30 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_service_timetable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='timetable',
            field=models.TextField(blank=True, default=dict),
        ),
    ]
