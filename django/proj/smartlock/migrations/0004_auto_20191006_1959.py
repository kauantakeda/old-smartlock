# Generated by Django 2.2.4 on 2019-10-06 22:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartlock', '0003_unlockattemptlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='unlockattemptlog',
            name='lockid',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='unlockattemptlog',
            name='rfid',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='unlockattemptlog',
            name='succ',
            field=models.BooleanField(default=None),
            preserve_default=False,
        ),
    ]
