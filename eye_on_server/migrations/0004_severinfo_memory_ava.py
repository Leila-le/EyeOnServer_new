# Generated by Django 4.2.3 on 2023-07-31 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0003_alter_severinfo_cpu_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='severinfo',
            name='memory_ava',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
