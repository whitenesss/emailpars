# Generated by Django 5.1 on 2024-09-01 03:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsers', '0002_rename_emailmassage_emailmessage'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailmessage',
            name='uid',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]