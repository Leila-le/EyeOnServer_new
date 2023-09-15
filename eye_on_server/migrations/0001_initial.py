# Generated by Django 4.2.3 on 2023-09-15 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=50, unique=True)),
                ('nickname', models.CharField(max_length=50, null=True)),
                ('create_at', models.DateTimeField(auto_now_add=True)),
                ('update_at', models.DateTimeField(auto_now=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='SeverInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=30, null=True)),
                ('license_name', models.CharField(blank=True, max_length=30, null=True)),
                ('time', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_guest', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_guest_nice', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_idle', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_iowait', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_irq', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_nice', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_percent', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_softirq', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_steal', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_system', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_total_active', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_total_idle', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_user', models.CharField(blank=True, max_length=30, null=True)),
                ('cpu_count', models.CharField(blank=True, max_length=5, null=True)),
                ('memory_free_physics', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_free_swap', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_processes', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_total_physics', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_total_swap', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_uptime', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_used_physics', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_used_swap', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_ava', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_percent', models.CharField(blank=True, max_length=30, null=True)),
                ('memory_swap_percent', models.CharField(blank=True, max_length=30, null=True)),
                ('disk_free', models.CharField(blank=True, max_length=30, null=True)),
                ('disk_mount_point', models.CharField(blank=True, max_length=30, null=True)),
                ('disk_total', models.CharField(blank=True, max_length=30, null=True)),
                ('disk_used', models.CharField(blank=True, max_length=30, null=True)),
                ('disk_percent', models.CharField(blank=True, max_length=30, null=True)),
            ],
        ),
    ]
