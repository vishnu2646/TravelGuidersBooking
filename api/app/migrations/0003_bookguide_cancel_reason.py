# Generated by Django 5.1.1 on 2024-09-26 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_rename_guide_bookguide_guide_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookguide',
            name='cancel_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
