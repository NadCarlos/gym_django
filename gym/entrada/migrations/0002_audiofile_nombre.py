# Generated by Django 4.2.11 on 2024-08-16 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entrada', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audiofile',
            name='nombre',
            field=models.CharField(default='E', max_length=50),
        ),
    ]
