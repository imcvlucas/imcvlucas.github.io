# Generated by Django 4.0.6 on 2022-09-20 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentalapp', '0015_remove_myuser_address_remove_myuser_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='stripe_price_id',
            field=models.CharField(default='', max_length=200),
        ),
    ]
