# Generated by Django 4.1.7 on 2023-04-11 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=100)),
                ('description', models.CharField(max_length=100)),
                ('creator', models.CharField(max_length=100)),
                ('status', models.IntegerField()),
                ('type', models.IntegerField()),
                ('severity', models.IntegerField()),
                ('priority', models.IntegerField()),
                ('creationdate', models.DateTimeField(auto_now_add=True)),
                ('modifieddate', models.DateTimeField(auto_now=True)),
                ('deadlinedate', models.DateTimeField(blank=True, null=True)),
                ('deadlinemotive', models.CharField(max_length=100)),
            ],
        ),
    ]
