# Generated by Django 5.1.3 on 2024-11-10 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auto_bid', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemuserinput',
            name='items_in_bid_group',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='itemuserinput',
            name='items_in_bid_group_won',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
