# Generated by Django 4.2.3 on 2023-09-19 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eye_on_server', '0005_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='severinfo',
            name='alter_query',
            field=models.BooleanField(default=False),
        ),
    ]
