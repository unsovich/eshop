# Generated by Django 4.2.6 on 2023-10-26 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]