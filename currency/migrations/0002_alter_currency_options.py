# Generated by Django 4.2.3 on 2024-06-18 06:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='currency',
            options={'verbose_name_plural': 'Currency'},
        ),
    ]