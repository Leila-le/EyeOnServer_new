# Generated by Django 4.2.3 on 2023-09-21 08:49

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='severinfo',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]