# Generated by Django 5.1.4 on 2025-01-12 23:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='finalmessage',
            name='content',
        ),
        migrations.RemoveField(
            model_name='finalmessage',
            name='created_at',
        ),
    ]
