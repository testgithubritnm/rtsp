# Generated by Django 4.2.11 on 2024-04-24 09:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_delete_rtspurl_camera_rtsp_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='camera',
            name='model',
        ),
    ]