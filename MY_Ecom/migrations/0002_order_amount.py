# Generated by Django 3.2.9 on 2021-12-23 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MY_Ecom', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='Amount',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
