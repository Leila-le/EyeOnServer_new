# Generated by Django 4.2.3 on 2023-10-12 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='severinfo',
            name='time',
            field=models.DateTimeField(),
        ),
    ]
