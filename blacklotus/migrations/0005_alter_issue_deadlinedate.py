# Generated by Django 4.1.7 on 2023-04-11 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blacklotus', '0004_issue_blocked_issue_blockmotive_issue_deadline_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='deadlinedate',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]