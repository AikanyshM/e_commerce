# Generated by Django 3.2 on 2022-06-03 14:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_auto_20220603_1340'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('item', 'session_key', 'ordered')},
        ),
    ]