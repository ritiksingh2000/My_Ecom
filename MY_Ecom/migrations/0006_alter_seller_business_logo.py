# Generated by Django 3.2.9 on 2021-12-07 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MY_Ecom', '0005_seller_business_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seller',
            name='Business_Logo',
            field=models.ImageField(default='upload/seller/logo/default_logo.png', upload_to='seller/logo'),
        ),
    ]
