# Generated by Django 5.1.3 on 2024-12-01 04:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authenticator', '0002_alter_authenticator_table_alter_user_table'),
    ]

    operations = [
        migrations.RenameField(
            model_name='authenticator',
            old_name='reset_token',
            new_name='refresh_token',
        ),
    ]
