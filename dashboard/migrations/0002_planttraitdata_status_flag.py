# Generated by Django 5.2.3 on 2025-07-12 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='planttraitdata',
            name='status_flag',
            field=models.CharField(blank=True, choices=[('🕓', 'Too Early'), ('⏳', 'Due Soon'), ('❌', 'Overdue'), ('✔️', 'Completed')], max_length=10, null=True),
        ),
    ]
