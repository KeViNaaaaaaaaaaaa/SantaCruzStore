# Generated by Django 5.1.4 on 2024-12-16 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0005_promocode'),
    ]

    operations = [
        migrations.AddField(
            model_name='promocode',
            name='val_of_activate',
            field=models.PositiveIntegerField(default=1),
        ),
    ]