# Generated by Django 2.2.4 on 2019-11-05 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('smartlock', '0018_auto_20191103_1445'),
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_strt', models.DateField(verbose_name='starting date')),
                ('dt_stop', models.DateField(verbose_name='ending date')),
                ('tm_strt', models.TimeField(blank=True, null=True, verbose_name='starting time')),
                ('tm_stop', models.TimeField(blank=True, null=True, verbose_name='ending time')),
                ('mond', models.BooleanField(default=False, verbose_name='monday')),
                ('tues', models.BooleanField(default=False, verbose_name='tuesday')),
                ('wedn', models.BooleanField(default=False, verbose_name='wednesday')),
                ('thur', models.BooleanField(default=False, verbose_name='thursday')),
                ('frid', models.BooleanField(default=False, verbose_name='friday')),
                ('satu', models.BooleanField(default=False, verbose_name='saturday')),
                ('sund', models.BooleanField(default=False, verbose_name='sunday')),
                ('lock', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='smartlock.Lock')),
                ('lockgrup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='smartlock.LockGroup', verbose_name='lock group')),
                ('userdata', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='smartlock.UserData')),
                ('userdatagrup', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='smartlock.UserDataGroup', verbose_name='user data group')),
            ],
            options={
                'unique_together': {('userdata', 'lock'), ('userdatagrup', 'lock'), ('userdata', 'lockgrup'), ('userdatagrup', 'lockgrup')},
            },
        ),
    ]
