# Generated by Django 2.2.4 on 2019-10-05 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('smartlock', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lock',
            name='ipv4',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='lock',
            name='name',
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='lockgroup',
            name='name',
            field=models.CharField(max_length=150, unique=True),
        ),
        migrations.AlterField(
            model_name='userdatagroup',
            name='name',
            field=models.CharField(max_length=150, unique=True),
        ),
    ]
