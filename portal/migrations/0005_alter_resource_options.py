# Generated by Django 5.0.4 on 2024-04-25 22:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_resource'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resource',
            options={'ordering': ['-date_shared']},
        ),
    ]
