# Generated by Django 5.0.1 on 2024-02-17 08:27

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
                ('ip_domain_name', models.CharField(max_length=255)),
                ('port', models.IntegerField(default=80)),
                ('device_type', models.CharField(max_length=50)),
                ('channel_number', models.IntegerField()),
                ('serial_number', models.CharField(max_length=50)),
                ('operation', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('device_model', models.CharField(max_length=50)),
                ('rtsp_url', models.CharField(max_length=255)),
            ],
        ),
    ]