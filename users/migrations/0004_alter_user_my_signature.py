# Generated by Django 5.0.7 on 2024-08-27 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_my_signature'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='my_signature',
            field=models.FileField(blank=True, null=True, upload_to='signatures/'),
        ),
    ]
