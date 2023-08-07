# Generated by Django 4.2.3 on 2023-08-07 09:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0008_rename_guest_severinfo_cpu_guest_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LicenseName',
        ),
        migrations.RenameField(
            model_name='severinfo',
            old_name='ip',
            new_name='license_name',
        ),
        migrations.RenameField(
            model_name='severinfo',
            old_name='mem_used',
            new_name='memory_percent',
        ),
        migrations.RenameField(
            model_name='severinfo',
            old_name='memory_per',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='severinfo',
            name='memory_total',
        ),
    ]
