# Generated by Django 5.1.4 on 2024-12-11 06:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0010_remove_order_user_remove_orderitem_order_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
