# Generated by Django 4.2.3 on 2024-01-04 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bigdealapp', '0008_coupon_couponhistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='usageLimit',
            field=models.PositiveIntegerField(default=0, verbose_name='Usage Limit'),
        ),
    ]