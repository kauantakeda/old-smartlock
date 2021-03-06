# Generated by Django 2.2.4 on 2019-11-03 16:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smartlock', '0015_timezone'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='timezone',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='lock',
            name='tmzn',
            field=models.ForeignKey(default=198, on_delete=django.db.models.deletion.PROTECT, to='smartlock.TimeZone'),
            preserve_default=False,
        ),
    ]
