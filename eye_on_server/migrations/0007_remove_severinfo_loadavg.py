# Generated by Django 4.2.3 on 2023-09-26 09:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0006_remove_severinfo_alter_query'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='severinfo',
            name='loadavg',
        ),
    ]
