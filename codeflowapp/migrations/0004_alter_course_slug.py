# Generated by Django 5.1.2 on 2024-11-11 23:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeflowapp', '0003_populate_course_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]
