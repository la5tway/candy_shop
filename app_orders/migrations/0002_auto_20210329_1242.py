# Generated by Django 3.1.7 on 2021-03-29 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='weight',
            field=models.FloatField(verbose_name='Вес заказа'),
        ),
    ]
