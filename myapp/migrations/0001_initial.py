# Generated by Django 4.2.11 on 2024-03-14 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Camera',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('camera_name', models.CharField(max_length=100, unique=True)),
                ('ip', models.CharField(max_length=255)),
                ('port', models.IntegerField(default=80)),
                ('device_type', models.CharField(blank=True, max_length=50)),
                ('channel_number', models.IntegerField(default=1)),
                ('operation', models.CharField(blank=True, max_length=50)),
                ('status', models.BooleanField(blank=True, default=True)),
                ('device_model', models.CharField(blank=True, max_length=50)),
                ('username', models.CharField(blank=True, max_length=100)),
                ('password', models.CharField(blank=True, max_length=100)),
                ('model', models.CharField(blank=True, max_length=100)),
                ('serial_number', models.CharField(blank=True, max_length=100)),
                ('firmware_version', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RTSPUrl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=255)),
            ],
        ),
    ]
