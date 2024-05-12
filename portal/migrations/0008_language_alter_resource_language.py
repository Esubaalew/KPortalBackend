# Generated by Django 4.2.11 on 2024-05-12 14:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0007_follow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('shorty', models.CharField(max_length=100)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='resource',
            name='language',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portal.language'),
        ),
    ]