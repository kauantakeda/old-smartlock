# Generated by Django 2.2.4 on 2019-10-17 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smartlock', '0006_auto_20191010_1426'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lockpermission',
            unique_together={('userdata', 'lock'), ('userdatagrup', 'lockgrup'), ('userdata', 'lockgrup'), ('userdatagrup', 'lock')},
        ),
    ]
