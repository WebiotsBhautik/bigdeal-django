# Generated by Django 4.2.3 on 2023-07-11 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bigdealapp', '0002_blog_blogcategory_blogcomment_blog_blogcategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='bannerImageTwo',
            field=models.ImageField(blank=True, null=True, upload_to='fashion/banner', verbose_name='Optional Image'),
        ),
    ]
