# Generated by Django 4.0.3 on 2023-06-20 07:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0020_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='value',
        ),
    ]