# Generated by Django 4.2.3 on 2023-09-27 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_cart_cart_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
    ]
