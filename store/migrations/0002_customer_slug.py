# Generated by Django 5.1.4 on 2024-12-08 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='slug',
            field=models.SlugField(default='-'),
        ),
    ]
