# Generated by Django 2.0.1 on 2019-01-15 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy_ticket', '0012_pushdeployment_build_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='selected_for_push_deployment',
            field=models.BooleanField(default=False),
        ),
    ]
