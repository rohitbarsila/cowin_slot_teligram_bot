# Generated by Django 3.2.2 on 2021-05-11 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teleBot', '0004_teligram_user_can_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='teligram_user',
            name='deregister',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='teligram_user',
            name='can_add',
            field=models.BooleanField(default=True),
        ),
    ]
