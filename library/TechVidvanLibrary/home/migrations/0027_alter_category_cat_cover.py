# Generated by Django 4.0.3 on 2023-06-26 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_category_addbook_quantity_alter_addbook_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='cat_cover',
            field=models.ImageField(upload_to='category_cover/'),
        ),
    ]
