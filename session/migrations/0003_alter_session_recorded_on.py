# Generated by Django 4.0 on 2021-12-28 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('session', '0002_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='recorded_on',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
