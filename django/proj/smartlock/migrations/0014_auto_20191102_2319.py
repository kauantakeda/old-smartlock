# Generated by Django 2.2.4 on 2019-11-03 02:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smartlock', '0013_auto_20191102_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lockpermissionschedule',
            name='perm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='smartlock.LockPermission'),
        ),
    ]