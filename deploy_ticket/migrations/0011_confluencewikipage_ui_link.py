# Generated by Django 2.0.1 on 2019-01-15 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deploy_ticket', '0010_confluencewikipage_page_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='confluencewikipage',
            name='ui_link',
            field=models.URLField(blank=True, null=True),
        ),
    ]
