# Generated by Django 4.2.3 on 2023-08-16 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0011_severinfo_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='severinfo',
            name='memory_swap_percent',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]