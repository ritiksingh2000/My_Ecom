# Generated by Django 3.2.9 on 2021-12-18 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MY_Ecom', '0020_order_paymentstatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='To',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]