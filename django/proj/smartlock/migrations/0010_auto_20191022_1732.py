# Generated by Django 2.2.6 on 2019-10-22 20:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('smartlock', '0009_auto_20191022_1708'),
    ]

    operations = [
        migrations.RenameField(
            model_name='unlockattemptlog',
            old_name='lockid',
            new_name='ruid',
        ),
    ]
