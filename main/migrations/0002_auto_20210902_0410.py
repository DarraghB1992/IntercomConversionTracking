# Generated by Django 3.2.7 on 2021-09-02 04:10

from django.db import migrations
import django_unixdatetimefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='conversation_closed_at',
            field=django_unixdatetimefield.fields.UnixDateTimeField(),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='conversation_created_at',
            field=django_unixdatetimefield.fields.UnixDateTimeField(),
        ),
    ]
