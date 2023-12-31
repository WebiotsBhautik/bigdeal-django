# Generated by Django 4.2.3 on 2023-07-07 05:29

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('product', '0002_attributename_attributevalue_product_productvariant_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BannerTheme',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bannerThemeName', models.CharField(max_length=250, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'verbose_name': 'Theme',
            },
        ),
        migrations.CreateModel(
            name='BannerType',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bannerTypeName', models.CharField(max_length=250, verbose_name='Name')),
                ('slug', models.SlugField(blank=True, unique=True)),
            ],
            options={
                'verbose_name': 'Banner Type',
            },
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('bannerImage', models.ImageField(upload_to='fashion/banner', verbose_name='Image')),
                ('titleOne', models.CharField(max_length=255, verbose_name='Title One')),
                ('titleTwo', models.CharField(blank=True, max_length=255, verbose_name='Title Two')),
                ('titleThree', models.CharField(blank=True, max_length=255, verbose_name='Title Three')),
                ('titleFour', models.CharField(blank=True, max_length=255, verbose_name='Title Four')),
                ('bannerProduct', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.productvariant', verbose_name='Product')),
                ('bannerTheme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigdealapp.bannertheme', verbose_name='Theme')),
                ('bannerType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bigdealapp.bannertype', verbose_name='Type')),
            ],
            options={
                'verbose_name': 'Banner',
            },
        ),
    ]
