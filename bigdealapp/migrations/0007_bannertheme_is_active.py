# Generated by Django 4.2.3 on 2023-10-04 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bigdealapp', '0006_contactus_alter_blog_popularblog'),
    ]

    operations = [
        migrations.AddField(
            model_name='bannertheme',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Status'),
        ),
    ]
