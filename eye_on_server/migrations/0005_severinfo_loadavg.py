# Generated by Django 4.2.3 on 2023-09-25 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0004_alter_severinfo_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='severinfo',
            name='loadavg',
            field=models.CharField(blank=True, max_length=5, null=True),
        ),
    ]
